from flask import Flask, render_template

app = Flask(__name__)

# 模拟足球比赛数据（实际应从API获取，如API-Football）
matches = [
    {"home": "皇家马德里", "away": "巴塞罗那", "league": "西甲", "win_prob": "45%", "draw_prob": "25%", "loss_prob": "30%", "prediction": "主胜"},
    {"home": "曼城", "away": "阿森纳", "league": "英超", "win_prob": "50%", "draw_prob": "20%", "loss_prob": "30%", "prediction": "大球"},
    {"home": "拜仁慕尼黑", "away": "多特蒙德", "league": "德甲", "win_prob": "60%", "draw_prob": "15%", "loss_prob": "25%", "prediction": "主胜"},
]

@app.route('/')
def home():
    return render_template('index.html', matches=matches)

if __name__ == '__main__':
    app.run(debug=True)