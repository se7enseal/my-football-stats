from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    # 模拟数据：实际开发时，这里会通过爬虫或API获取
    matches = [
        {
            "time": "2026-04-24 03:00",
            "league": "英超",
            "home": "曼城",
            "away": "阿森纳",
            "home_odds": "1.85",
            "draw_odds": "3.40",
            "away_odds": "4.20",
            "injuries": "曼城: 德布劳内(疑); 阿森纳: 萨利巴(伤)",
            "lineup": "双方主力阵容齐整，预计 4-3-3 对阵 4-2-3-1",
            "win_prob": "55%",
            "draw_prob": "25%",
            "loss_prob": "20%",
            "prediction": "主胜",
            "analysis": "曼城主场强势，近期豪取5连胜，历史交锋占据绝对优势。阿森纳后防核心缺阵，压力巨大。"
        },
        {
            "time": "2026-04-24 21:30",
            "league": "德甲",
            "home": "拜仁慕尼黑",
            "away": "多特蒙德",
            "home_odds": "1.50",
            "draw_odds": "4.50",
            "away_odds": "5.50",
            "injuries": "拜仁: 诺伊尔(伤); 多特: 无主要伤停",
            "lineup": "拜仁预计全主力出击，寻求主场连胜",
            "win_prob": "65%",
            "draw_prob": "20%",
            "loss_prob": "15%",
            "prediction": "大球",
            "analysis": "国家德比一向进球较多，两队进攻火力全开，建议关注进球数。"
        }
    ]
    return render_template('index.html', matches=matches)

if __name__ == '__main__':
    app.run(debug=True)