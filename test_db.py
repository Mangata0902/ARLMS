import os
import sys
from sqlalchemy import create_engine, text

# 1. 手动填入你的数据库信息 (请修改这里！)
# 格式: postgresql://用户名:密码@localhost:5432/数据库名
DB_URL = "postgresql://postgres:20050902@localhost:5432/arlms_db"

try:
    print(f"--- 🔍 正在尝试连接: {DB_URL.split('@')[-1]} ---") # 打印地址(隐藏密码)
    
    # 2. 直接创建引擎，不走 .env
    engine = create_engine(DB_URL)
    
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        version = result.fetchone()
        print("✅ [成功] Python 已成功连接到 PostgreSQL!")
        print(f"📊 [数据库版本]: {version[0]}")
        print("--- 🚀 你的‘水电’已通 ---")

except Exception as e:
    print(f"❌ 连接失败！错误详情:\n{e}")
    print("\n💡 请检查:")
    print("1. 你的密码是否正确？")
    print("2. 数据库名 'arlms_db' 是否已经在 pgAdmin 里创建了？")
    print("3. PostgreSQL 服务是否正在运行？")
