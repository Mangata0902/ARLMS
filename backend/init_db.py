import sys
import os
from pathlib import Path

# 1. 确保 Python 能找到 app 目录
current_dir = Path(__file__).resolve().parent # backend 目录
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

# 2. 修正导入路径
try:
    from app.core.database import engine, Base
    # ✨ 关键：必须导入 ResearchProject，否则表不会创建
    from app.models.all_models import (
        Category, User, Material, MaterialItem, Loan, Fine, 
        Reservation, AIReadAnalytic, SemanticTag, Conversation, 
        UserInterest, MentorStudent, ResearchProject  # <--- 添加这一行
    )
    print("✅ 模块导入成功")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

def create_tables():
    print("🚀 正在初始化数据库...")
    try:
        # 自动创建所有定义的表
        Base.metadata.create_all(bind=engine)
        print("✅ 恭喜！所有表（包括 ResearchProject）已成功创建/更新。")
        
        # 检查是 PostgreSQL 还是 SQLite
        db_url = str(engine.url)
        if "postgresql" in db_url:
            print(f"🔗 当前连接到 PostgreSQL 数据库: {db_url.split('@')[-1]}")
        else:
            print(f"📂 当前连接到 SQLite 数据库: {current_dir / 'sql_app.db'}")
            
    except Exception as e:
        print(f"❌ 创建失败，错误原因: {e}")

if __name__ == "__main__":
    create_tables()
