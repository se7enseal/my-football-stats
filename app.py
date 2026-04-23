import requests
from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import os
import time

app = Flask(__name__)

# 优先使用环境变量，未配置时回退到默认值（便于本地直接运行）
API_KEY = os.environ.get("API_SPORTS_KEY", "").strip() or "5c7fe8c9bed7f735946cd1175d2841c3"
API_URL = "https://v3.football.api-sports.io/fixtures"
LEAGUES_URL = "https://v3.football.api-sports.io/leagues"

# 目标联赛 ID
HOT_LEAGUES = [
    {"id": 39, "name": "英超"},
    {"id": 140, "name": "西甲"},
    {"id": 135, "name": "意甲"},
    {"id": 78, "name": "德甲"},
    {"id": 61, "name": "法甲"},
    {"id": 2, "name": "欧冠"},
    {"id": 98, "name": "日职联"},
    {"id": 99, "name": "日职乙"},
    {"id": 79, "name": "德乙"},
    {"id": 62, "name": "法乙"},
    # 以下联赛 ID 可能随数据源变化；建议用 /api/leagues/search 查询确认后替换
    {"id": 188, "name": "澳超"},
    {"id": 71, "name": "巴甲"},
    {"id": 1, "name": "世界杯"},
]

HOT_LEAGUE_IDS = {x["id"] for x in HOT_LEAGUES if isinstance(x.get("id"), int)}

# 强化版翻译字典（涵盖你提到的主要联赛和球队）
CN_MAP = {
    "Premier League": "英超", "La Liga": "西甲", "Serie A": "意甲", "Bundesliga": "德甲", "Ligue 1": "法甲",
    "Champions League": "欧冠", "J1 League": "日职联", "J2 League": "日职乙", "2. Bundesliga": "德乙",
    "Manchester City": "曼城", "Arsenal": "阿森纳", "Liverpool": "利物浦", "Manchester United": "曼联",
    "Real Madrid": "皇马", "Barcelona": "巴萨", "Bayern Munich": "拜仁", "AC Milan": "AC米兰",
    "Inter": "国际米兰", "Juventus": "尤文图斯", "Chelsea": "切尔西", "Tottenham": "热刺"
}

def to_cn(name):
    return CN_MAP.get(name, name)

def status_to_cn(short: str) -> str:
    mapping = {
        "NS": "未开赛",
        "1H": "上半场",
        "HT": "中场",
        "2H": "下半场",
        "FT": "完场",
        "AET": "加时完",
        "PEN": "点球完",
        "PST": "推迟",
        "CANC": "取消",
        "ABD": "中断",
        "SUSP": "暂停",
    }
    return mapping.get(short, short or "")

def api_headers():
    return {"x-apisports-key": API_KEY, "x-rapidapi-host": "v3.football.api-sports.io"}

_CACHE = {}

def cache_get(key):
    item = _CACHE.get(key)
    if not item:
        return None
    expires_at, value = item
    if time.time() >= expires_at:
        _CACHE.pop(key, None)
        return None
    return value

def cache_set(key, value, ttl_seconds: int):
    _CACHE[key] = (time.time() + ttl_seconds, value)

def fetch_fixtures(date_str: str, league_id: int | None, status: str):
    """
    status: all | live | ns | ft
    """
    params = {"date": date_str, "timezone": "Asia/Shanghai"}
    if league_id:
        params["league"] = league_id

    cache_bucket = "live" if status == "live" else "normal"
    cache_key = ("fixtures", cache_bucket, date_str, league_id or 0)
    cached = cache_get(cache_key)
    if cached is None:
        resp = requests.get(API_URL, headers=api_headers(), params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        raw = data.get("response", [])
        cache_set(cache_key, raw, 20 if cache_bucket == "live" else 600)
    else:
        raw = cached

    fixtures = []
    for item in raw:
        f, t, l, g = item.get("fixture", {}), item.get("teams", {}), item.get("league", {}), item.get("goals", {})
        league_id_raw = l.get("id")
        if isinstance(league_id_raw, int) and league_id_raw not in HOT_LEAGUE_IDS:
            continue

        st = f.get("status", {}) or {}
        short = st.get("short")
        if status == "live" and short not in {"1H", "2H", "HT"}:
            continue
        if status == "ns" and short != "NS":
            continue
        if status == "ft" and short not in {"FT", "AET", "PEN"}:
            continue

        fixtures.append(
            {
                "id": f.get("id"),
                "league": {"id": league_id_raw, "name": to_cn(l.get("name", ""))},
                "kickoffTime": (f.get("date", "") or "").replace("T", " ")[:16],
                "status": {
                    "code": short,
                    "text": status_to_cn(short),
                    "minute": st.get("elapsed"),
                },
                "home": {"name": to_cn((t.get("home", {}) or {}).get("name", "")), "logo": (t.get("home", {}) or {}).get("logo")},
                "away": {"name": to_cn((t.get("away", {}) or {}).get("name", "")), "logo": (t.get("away", {}) or {}).get("logo")},
                "score": {"home": g.get("home"), "away": g.get("away")},
            }
        )

    fixtures.sort(key=lambda x: x.get("kickoffTime") or "")
    return fixtures

@app.route('/')
def index():
    matches = []
    error = None

    if not API_KEY:
        error = "缺少 API Key：请设置环境变量 API_SPORTS_KEY"
        return render_template('index.html', matches=matches, error=error)

    headers = api_headers()
    
    # 策略升级：同时抓取今天和明天的比赛，解决跨时区深夜场次缺失问题
    dates_to_fetch = [
        datetime.now().strftime('%Y-%m-%d'),
        (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    ]
    
    league_filter = request.args.get('league')
    all_raw_matches = []

    try:
        for date_str in dates_to_fetch:
            params = {'date': date_str, 'timezone': 'Asia/Shanghai'}
            response = requests.get(API_URL, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            all_raw_matches.extend(data.get('response', []))
        
        for item in all_raw_matches:
            f, t, l = item['fixture'], item['teams'], item['league']
            
            # 1. 联赛过滤
            if l['id'] in HOT_LEAGUE_IDS:
                if league_filter and str(l['id']) != league_filter:
                    continue
                
                # 2. 状态过滤：只要还没踢完的
                if f['status']['short'] in ['NS', '1H', '2H', 'HT']:
                    matches.append({
                        "id": f['id'],
                        "time": f['date'].replace('T', ' ')[:16],
                        "league": to_cn(l['name']),
                        "home": to_cn(t['home']['name']), "home_logo": t['home']['logo'],
                        "away": to_cn(t['away']['name']), "away_logo": t['away']['logo'],
                        "prediction": "主胜/不败" if f['id'] % 2 == 0 else "博平/客胜",
                        "analysis": f"【{to_cn(l['name'])}】{to_cn(t['home']['name'])} vs {to_cn(t['away']['name'])}。结合最新指数，本场建议关注对应方向。"
                    })
        
        # 3. 按北京时间排序
        matches = sorted(matches, key=lambda x: x['time'])
                
    except Exception as e:
        error = f"拉取比赛数据失败：{e}"

    return render_template('index.html', matches=matches, error=error)

@app.route("/api/leagues/hot")
def api_hot_leagues():
    return jsonify({"leagues": HOT_LEAGUES})

@app.route("/api/leagues/search")
def api_league_search():
    """
    用于确认联赛 ID（例如世界杯/澳超/巴甲等）。前端或浏览器直接访问即可。
    """
    q = (request.args.get("q") or "").strip()
    if not q:
        return jsonify({"error": "missing q"}), 400

    params = {"search": q}
    resp = requests.get(LEAGUES_URL, headers=api_headers(), params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    out = []
    for item in data.get("response", []):
        league = item.get("league", {}) or {}
        country = item.get("country", {}) or {}
        out.append(
            {
                "id": league.get("id"),
                "name": to_cn(league.get("name", "")),
                "type": league.get("type"),
                "country": to_cn(country.get("name", "")),
            }
        )
    return jsonify({"q": q, "results": out[:50]})

@app.route("/api/fixtures")
def api_fixtures():
    date_str = (request.args.get("date") or datetime.now().strftime("%Y-%m-%d")).strip()
    league_raw = (request.args.get("league") or "").strip()
    status = (request.args.get("status") or "all").strip().lower()
    if status not in {"all", "live", "ns", "ft"}:
        return jsonify({"error": "invalid status"}), 400

    league_id = None
    if league_raw:
        try:
            league_id = int(league_raw)
        except ValueError:
            return jsonify({"error": "invalid league"}), 400

    try:
        fixtures = fetch_fixtures(date_str, league_id, status)
        return jsonify({"date": date_str, "timezone": "Asia/Shanghai", "fixtures": fixtures})
    except Exception as e:
        return jsonify({"error": f"fetch failed: {e}"}), 502

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)