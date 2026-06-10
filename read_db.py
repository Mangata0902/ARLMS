import sqlite3
import os

def check_database():
    # 自动尝试两个可能的路径
    possible_paths = [
        'backend/sql_app.db',
        'sql_app.db',
        '../backend/sql_app.db'
    ]
    
    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ 找不到 sql_app.db 文件！请确认文件到底在哪个文件夹下。")
        return

    print(f"🔍 正在读取数据库: {os.path.abspath(db_path)}\n")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 先看看库里有哪些表，方便调试
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"现有表: {[t[0] for t in tables]}")

        query = """
        SELECT 
            m.id, 
            m.file_name, 
            a.content
        FROM materials m 
        LEFT JOIN ai_read_analytics a ON m.id = a.material_id 
        ORDER BY m.id DESC 
        LIMIT 1
        """
        
        cursor.execute(query)
        row = cursor.fetchone()

        if row:
            print(f"\n✅ 找到最新记录 (ID: {row[0]})")
            print(f"📄 文件名: {row[1]}")
            print("-" * 50)
            print(f"🤖 AI 解析内容:\n{row[2] if row[2] else '⚠️ 字段为空'}")
        else:
            print("\n❌ 数据库表中没有数据。")

        conn.close()
    except Exception as e:
        print(f"❌ 出错了: {e}")

if __name__ == "__main__":
    check_database()