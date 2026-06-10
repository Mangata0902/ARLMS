import uvicorn
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 1. 导入数据库初始化工具和模型
from app.core.database import engine, Base
from app.models.all_models import Base # 导入 Base 也会顺带加载该文件下的所有类 

# 2. 导入 API 路由 (✨ 统一使用 router 别名，干净清爽)
from app.api.auth import router as auth_router
from app.api.research import router as research_router
from app.api.ingestion import router as ingestion_router
from app.api.chat import router as chat_router
from app.api.materials import router as materials_router  # ✨ 新增的 materials 路由
from app.api.ai_detection import router as ai_router
from app.api.revision import router as revision_router

# 自动创建数据库表
print(f"📂 正在初始化数据库... 路径: {os.path.abspath('sql_app.db')}")
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="学术导师 AI 系统",
    description="基于 DeepSeek 的学术文档深度解析后端",
    version="1.0.0"
)

# 3. 配置跨域 (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. 注册路由 (✨ 统一使用别名变量)
app.include_router(auth_router,     prefix="/api/v1/auth",      tags=["0. 用户系统"])
app.include_router(research_router, prefix="/api/v1/research",  tags=["1. 选题与大纲生成"])
app.include_router(ingestion_router,prefix="/api/v1",           tags=["2. 文献上传与解析"])
app.include_router(chat_router,     prefix="/api/v1",           tags=["3. 导师对话与RAG"])
app.include_router(materials_router,prefix="/api/v1/materials", tags=["4. 文献库管理"])
app.include_router(ai_router,       prefix="/api/v1/ai",        tags=["5. AI检测"])
app.include_router(revision_router, prefix="/api/v1",           tags=["6. 论文修改"])  


@app.get("/")
async def root():
    return {
        "message": "学术导师 AI 系统后端已启动", 
        "docs": "/docs",
        "db_path": os.path.abspath('sql_app.db')
    }

if __name__ == "__main__":
    # 启动命令
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
