## uni-app 前端（小程序 + 公众号H5）

### 运行方式（无需小程序 AppID 也可先测）
- 用 HBuilderX 打开本目录 `uniapp/`
- 运行到浏览器（H5）

### 配置后端地址
修改 `utils/config.js` 里的 `API_BASE_URL`：
- 本地：`http://127.0.0.1:5000`
- Render：填你的 Render 服务域名，例如 `https://xxx.onrender.com`
- 自有域名：`https://api.365score.live`

### 后端接口
- `GET /api/leagues/hot`
- `GET /api/fixtures?date=YYYY-MM-DD&league=39&status=all|live|ns|ft`

