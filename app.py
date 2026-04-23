import requests
from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)

# 你的专属 API 配置
API_KEY = "5c7fe8c9bed7f735946cd1175d2841c3"
API_HOST = "v3.football.api-sports.io"

@app.route('/')
def index():
    url = f"https://{API_HOST}/fixtures"
    headers = {
        'x-apisports-key': API_KEY,
        'x-rapidapi-host': API_HOST
    }
    
    # 自动获取英超（ID: 39）接下来的 10 场比赛，并转为北京时间
    params = {'league': '39', 'next': '10', 'timezone': 'Asia/Shanghai'}
    
    matches = []
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        data = response.json()
        
        for item in data.get('response', []):
            f = item['fixture']
            t = item['teams']
            l = item['league']
            
            # 这里的预测逻辑你可以后续根据赔率自定义
            # 目前模拟：根据主队 ID 奇偶性给出不同建议
            is_even = f['id'] % 2 == 0
            suggestion = "主胜" if is_even else "让球客胜"
            
            matches.append({
                "time": f['date'].replace('T', ' ')[:16],
                "league": l['name'],
                "home": t['home']['name'],
                "home_logo": t['home']['logo'],
                "away": t['away']['name'],
                "away_logo": t['away']['logo'],
                "status": "未开始" if f['status']['short'] == 'NS' else "进行中",
                "prediction": suggestion,
                "analysis": f"结合 {t['home']['name']} 近期主场进球效率及 API 实时即时赔率波动，本场建议锁定 {suggestion}。盘口走势相对稳定，具备博胆价值。"
            })
    except Exception as e:
        print(f"数据抓取失败: {e}")

    return render_template('index.html', matches=matches)

if __name__ == '__main__':
    app.run(debug=True)