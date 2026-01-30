"""
清空并重建数字客户数据库表

警告：此操作会删除所有数据！
运行前请确保已备份重要数据。

运行方式:
python backend/migrations/reset_digital_customer_db.py
"""
import sqlite3
import os

# 直接构建数据库路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(BACKEND_DIR, "data")
DIGITAL_CUSTOMER_DB_PATH = os.path.join(DATA_DIR, "digital_customer.db")


def reset_database():
    """清空并重建数据库"""
    print("=" * 60)
    print("⚠️  警告：即将清空数字客户数据库所有表！")
    print("=" * 60)
    print(f"数据库路径: {DIGITAL_CUSTOMER_DB_PATH}")

    if not os.path.exists(DIGITAL_CUSTOMER_DB_PATH):
        print(f"✅ 数据库文件不存在，将在应用启动时自动创建")
        return

    # 确认操作
    print("\n此操作将删除以下表的所有数据：")
    print("  - customer_profile_registry")
    print("  - customer_profiles")
    print("  - customer_chunks")
    print("  - chat_sessions")
    print("  - chat_messages")
    print("  - training_sessions")
    print("  - conversation_rounds")
    print("  - stage_evaluations")
    print("  - final_evaluations")
    print("  - sales_knowledge")

    confirm = input("\n确认删除所有数据？(输入 YES 继续): ")
    if confirm != "YES":
        print("❌ 操作已取消")
        return

    conn = sqlite3.connect(DIGITAL_CUSTOMER_DB_PATH)
    cursor = conn.cursor()

    try:
        print("\n开始清空数据库...")

        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        print(f"\n找到 {len(tables)} 个表")

        # 删除所有表
        for table in tables:
            table_name = table[0]
            if table_name != 'sqlite_sequence':  # 跳过系统表
                print(f"  删除表: {table_name}")
                cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

        conn.commit()

        print("\n" + "=" * 60)
        print("✅ 数据库已清空！")
        print("=" * 60)
        print("\n下一步：")
        print("1. 启动应用，系统会自动创建新表结构")
        print("2. 将客户画像文件放入 data/customer_profiles/ 目录")
        print("3. 应用启动时会自动导入文件")
        print("\n或者通过前端界面手动上传客户画像文件")
        print("=" * 60)

    except Exception as e:
        conn.rollback()
        print(f"\n❌ 操作失败: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    reset_database()
