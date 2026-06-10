import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from pathlib import Path

# 1. 定位并加载 .env 文件
# 确保你的 .env 文件在项目根目录，且包含 DATABASE_URL=postgresql://user:password@localhost:5432/dbname
env_path = Path(__file__).resolve().parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# 2. 获取数据库地址
# 生产环境下必须从环境变量读取，如果读取不到则抛出错误或提供一个明确的 PG 默认值
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:password@localhost:5432/arlms_db" # 请根据你的实际 PG 配置修改此处
)

# 3. 创建 PostgreSQL 引擎
# PostgreSQL 不需要 check_same_thread 参数
# pool_size: 连接池大小; max_overflow: 超过池大小后允许临时创建的连接数
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # 每次使用连接前先检查是否有效，防止“连接已断开”错误
    echo=False           # 如果想在控制台看到所有 SQL 语句，可以改为 True
)

# 4. 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 5. 创建基类
Base = declarative_base()

# 6. 获取数据库连接的生成器 (用于 FastAPI Depends)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
