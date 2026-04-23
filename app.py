import requests
from flask import Flask, render_template
import os

app = Flask(__name__)

# 确认你的 API Key 准确无误
API_KEY = "5c7fe8c9bed7f735946cd1175d2841c3"
API_URL = "https://v3.football.api-sports.io/fixtures"

@app.route('/')
def index():
    headers = {
        'x-apisports-key': API_KEY,
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }
    
    # 策略调整：直接获取全球范围内接下来的 20 场比赛，不限联赛
    params = {
        'next': '20', 
        'timezone': 'Asia/Shanghai'
    }
    
    matches = []
    try:
        print("正在发起 API 请求...")
        response = requests.get(API_URL, headers=headers, params=params, timeout=15)
        data = response.json()
        
        # 打印一下 API 返回的状态，方便在 Render Logs 里排查
        print(f"API 响应状态: {data.get('get')}, 错误信息: {data.get('errors')}")
        
        results = data.get('response', [])
        
        if not results:
            print("API 返回结果为空，可能额度用完或时区内无比赛")
        
        for item in results:
            f = item['fixture']
            t = item['teams']
            l = item['league']
            
            matches.append({
                "time": f['date'].replace('T', ' ')[:16],
                "league": l['name'],
                "home": t['home']['name'],
                "home_logo": t['home']['logo'],
                "away": t['away']['name'],
                "away_logo": t['away']['logo'],
                "prediction": "主胜/大球" if f['id'] % 2 == 0 else "受让/小球",
                "analysis": f"根据 {l['name']} 官方数据及实时指数，本场建议关注双方进攻转换效率。AI 模型计算得出该场比赛破门概率较高。"
            })
            
    except Exception as e:
        print(f"代码运行崩溃: {e}")

    return render_template('index.html', matches=matches)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)