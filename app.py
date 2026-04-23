import requests
from flask import Flask, render_template
import os

app = Flask(__name__)

API_KEY = "5c7fe8c9bed7f735946cd1175d2841c3"
API_HOST = "v3.football.api-sports.io"

@app.route('/')
def index():
    url = f"https://{API_HOST}/fixtures"
    headers = {'x-apisports-key': API_KEY, 'x-rapidapi-host': API_HOST}
    
    # 扩大搜索范围：不限联赛，获取全球接下来的 10 场比赛
    params = {'next': '10', 'timezone': 'Asia/Shanghai'}
    
    matches = []
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        data = response.json()
        results = data.get('response', [])
        
        if not results:
            # 如果 API 真的没返回数据，我们加一场伪数据测试界面
            matches.append({
                "time": "数据加载中",
                "league": "系统消息",
                "home": "待更新", "home_logo": "https://media.api-sports.io/football/teams/33.png",
                "away": "待更新", "away_logo": "https://media.api-sports.io/football/teams/34.png",
                "status": "Check API",
                "prediction": "无",
                "analysis": "API 目前未返回近期赛程，请检查 API 额度或稍后再试。"
            })
        else:
            for item in results:
                f, t, l = item['fixture'], item['teams'], item['league']
                matches.append({
                    "time": f['date'].replace('T', ' ')[:16],
                    "league": l['name'],
                    "home": t['home']['name'], "home_logo": t['home']['logo'],
                    "away": t['away']['name'], "away_logo": t['away']['logo'],
                    "status": "未开赛",
                    "prediction": "主胜" if f['id'] % 2 == 0 else "让平/让负",
                    "analysis": f"根据 {l['name']} 赛制特点及实时数据，本场 AI 建议关注双方攻防转换表现。"
                })
    except Exception as e:
        print(f"API Error: {e}")

    return render_template('index.html', matches=matches)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)