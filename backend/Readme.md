# ARLMS 学术论文 AI 平台 - 启动指南

## 1. 环境准备
- Python 3.9+
- Node.js 16+
- PostgreSQL 数据库 (需手动创建名为 `arlms_db` 的数据库)

## 2. 后端启动 (Backend)
1. 进入后端目录：`cd backend`
2. 创建虚拟环境：`python -m venv venv`
3. 激活虚拟环境：
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. 安装依赖：`pip install -r requirements.txt`
5. 配置数据库连接：修改 `config.py` 或 `main.py` 中的数据库 URL。
6. 启动服务：`python main.py`

## 3. 前端启动 (Frontend)
1. 进入前端目录：`cd frontend`
2. 安装依赖：`npm install`
3. 启动开发服务器：`npm run dev`

## 4. 访问地址
打开浏览器访问：`http://localhost:5173`