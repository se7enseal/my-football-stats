import requests
from flask import Flask, render_template, request
from datetime import datetime
import os

app = Flask(__name__)

API_KEY = "5c7fe8c9bed7f735946cd1175d2841c3"
API_URL = "https://v3.football.api-sports.io/fixtures"

# --- 目标联赛 ID 库 ---
# 欧冠(2), 英超(39), 西甲(140), 意甲(135), 德甲(78), 法甲(61)
# 葡超(94), 比甲(144), 德乙(79), 法乙(62), 日职联(98), 日职乙(99)
TARGET_LEAGUES = [2, 39, 140, 135, 78, 61, 94, 144, 79, 62, 98, 99]

CN_MAP = {
    "Champions League": "欧冠", "Premier League": "英超", "La Liga": "西甲", 
    "Serie A": "意甲", "Bundesliga": "德甲", "Ligue 1": "法甲",
    "Primeira Liga": "葡超", "J1 League": "日职联", "J2 League": "日职乙",
    "2. Bundesliga": "德乙", "Ligue 2": "法乙", "Belgian Pro League": "比甲"
}

@app.route('/')
def index():
    headers = {'x-apisports-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}
    
    # 自动校准北京时间
    today = datetime.now().strftime('%Y-%m-%d')
    params = {'date': today, 'timezone': 'Asia/Shanghai'} # 强制 API 层面校准
    
    # 获取筛选参数（左侧点击时使用）
    league_filter = request.args.get('league')
    
    matches = []
    try:
        response = requests.get(API_URL, headers=headers, params=params, timeout=15)
        data = response.json()
        results = data.get('response', [])
        
        for item in results:
            f, t, l = item['fixture'], item['teams'], item['league']
            l_id = l['id']
            
            # --- 核心过滤逻辑 ---
            # 1. 必须在目标联赛名单内
            # 2. 如果用户点击了左侧筛选，则额外匹配该 ID
            if l_id in TARGET_LEAGUES:
                if league_filter and str(l_id) != league_filter:
                    continue
                
                h_name = CN_MAP.get(t['home']['name'], t['home']['name'])
                a_name = CN_MAP.get(t['away']['name'], t['away']['name'])
                l_name = CN_MAP.get(l['name'], l['name'])
                
                matches.append({
                    "id": f['id'],
                    "time": f['date'].replace('T', ' ')[:16],
                    "league": l_name,
                    "home": h_name, "home_logo": t['home']['logo'],
                    "away": a_name, "away_logo": t['away']['logo'],
                    "prediction": "主不败" if f['id'] % 2 == 0 else "看好客队",
                    "analysis": f"本场 {l_name} 赛事由 {h_name} 对阵 {a_name}。系统已校准北京时间，建议关注即时指数波动。"
                })
        
        # 排序：按时间先后顺序排列
        matches = sorted(matches, key=lambda x: x['time'])
                
    except Exception as e:
        print(f"数据抓取失败: {e}")

    return render_template('index.html', matches=matches)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)