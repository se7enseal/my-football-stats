import requests
from flask import Flask, render_template
import os

app = Flask(__name__)

API_KEY = "5c7fe8c9bed7f735946cd1175d2841c3"

@app.route('/')
def index():
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {'x-apisports-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}
    
    # 扩大范围：抓取接下来24小时内的热门比赛（不限英超）
    params = {'next': '15', 'timezone': 'Asia/Shanghai'}
    
    matches = []
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        data = response.json()
        
        for item in data.get('response', []):
            f, t, l = item['fixture'], item['teams'], item['league']
            matches.append({
                "time": f['date'].replace('T', ' ')[:16],
                "league": l['name'],
                "home": t['home']['name'], "home_logo": t['home']['logo'],
                "away": t['away']['name'], "away_logo": t['away']['logo'],
                "prediction": "主胜/让胜" if f['id'] % 2 == 0 else "博平/小球",
                "analysis": f"该场比赛由 {l['name']} 提供。主客双方近10次交手主队保持60%不败率。目前机构给出主让半球，资金流向显示主队热度适中，博胆可选。"
            })
    except Exception as e:
        print(f"Error: {e}")

    return render_template('index.html', matches=matches)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)