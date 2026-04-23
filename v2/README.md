## v2（从头重建）

### 后端（Render）
- **Root Directory**: `v2/backend`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`
- **Env**: `API_SPORTS_KEY=你的key`

部署后可测试：
- `/api/health`（包含中文测试字段）
- `/api/leagues/hot`
- `/api/fixtures?status=all`

### 前端（uni-app）
在 `v2/frontend`（后续我会继续补齐）。

