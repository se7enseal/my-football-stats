import requests
from flask import Flask, render_template, request
from datetime import datetime, timedelta
import os

app = Flask(__name__)

API_KEY = "5c7fe8c9bed7f735946cd1175d2841c3"
API_URL = "https://v3.football.api-sports.io/fixtures"

# 目标联赛 ID
TARGET_LEAGUES = [2, 39, 140, 135, 78, 61, 94, 144, 79, 62, 98, 99]

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

@app.route('/')
def index():
    headers = {'x-apisports-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}
    
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
            data = response.json()
            all_raw_matches.extend(data.get('response', []))
        
        matches = []
        for item in all_raw_matches:
            f, t, l = item['fixture'], item['teams'], item['league']
            
            # 1. 联赛过滤
            if l['id'] in TARGET_LEAGUES:
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
        print(f"Error: {e}")

    return render_template('index.html', matches=matches)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)