import requests
from flask import Flask, render_template
from datetime import datetime
import os

app = Flask(__name__)

API_KEY = "5c7fe8c9bed7f735946cd1175d2841c3"
API_URL = "https://v3.football.api-sports.io/fixtures"

# 常用球队/联赛中文映射表（你可以根据需要随时在这里添加）
CN_MAP = {
    "Premier League": "英超", "La Liga": "西甲", "Serie A": "意甲", "Bundesliga": "德甲",
    "Real Madrid": "皇家马德里", "Barcelona": "巴塞罗那", "Manchester City": "曼城",
    "Arsenal": "阿森纳", "Liverpool": "利物浦", "Manchester United": "曼联",
    "Chelsea": "切尔西", "Bayern Munich": "拜仁慕尼黑", "AC Milan": "AC米兰"
}

def to_cn(name):
    return CN_MAP.get(name, name)

@app.route('/')
def index():
    headers = {'x-apisports-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}
    today = datetime.now().strftime('%Y-%m-%d')
    params = {'date': today, 'timezone': 'Asia/Shanghai'}
    
    matches = []
    try:
        response = requests.get(API_URL, headers=headers, params=params, timeout=15)
        data = response.json()
        results = data.get('response', [])
        
        for item in results:
            f, t, l = item['fixture'], item['teams'], item['league']
            
            # 过滤：只看还没开始或进行中的
            if f['status']['short'] in ['NS', '1H', '2H', 'HT']:
                h_name = to_cn(t['home']['name'])
                a_name = to_cn(t['away']['name'])
                l_name = to_cn(l['name'])
                
                matches.append({
                    "time": f['date'].replace('T', ' ')[:16], # 这里保留了年月日
                    "league": l_name,
                    "home": h_name, "home_logo": t['home']['logo'],
                    "away": a_name, "away_logo": t['away']['logo'],
                    "prediction": "主不败" if f['id'] % 2 == 0 else "看好客队",
                    # 动态生成战绩描述，不再死磕英超
                    "analysis": f"今日 {l_name} 焦点战。{h_name} 近期主场胜率稳定，面对 {a_name} 的防线压力较小。",
                    "history": [
                        {"date": "近期", "home": h_name, "score": "VS", "away": a_name, "res": "待战"}
                    ]
                })
    except Exception as e:
        print(f"Error: {e}")

    return render_template('index.html', matches=matches)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)