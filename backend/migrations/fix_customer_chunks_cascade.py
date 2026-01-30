"""
数据迁移: 修复 CustomerChunk 表的外键约束，添加级联删除

问题: customer_chunks 表的 customer_profile_id 外键缺少 CASCADE 删除
导致: 删除客户时失败，报错 NOT NULL constraint failed
原因: 第一次迁移重建 customer_profiles 表时破坏了外键关系

解决: 重建 customer_chunks 表并添加 CASCADE 约束

运行方式:
python backend/migrations/fix_customer_chunks_cascade.py
"""
import sqlite3
import os

# 直接构建数据库路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(BACKEND_DIR, "data")
DIGITAL_CUSTOMER_DB_PATH = os.path.join(DATA_DIR, "digital_customer.db")


def migrate():
    """修复 CustomerChunk 外键约束"""
    print("=" * 60)
    print("开始修复 customer_chunks 表外键约束...")
    print("=" * 60)
    print(f"数据库路径: {DIGITAL_CUSTOMER_DB_PATH}")

    if not os.path.exists(DIGITAL_CUSTOMER_DB_PATH):
        print(f"❌ 数据库文件不存在: {DIGITAL_CUSTOMER_DB_PATH}")
        return

    conn = sqlite3.connect(DIGITAL_CUSTOMER_DB_PATH)
    cursor = conn.cursor()

    try:
        # 检查表是否存在
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='customer_chunks'
        """)
        if not cursor.fetchone():
            print("⚠ customer_chunks 表不存在，跳过迁移")
            return

        print("步骤 1/5: 检查现有数据...")
        cursor.execute("SELECT COUNT(*) FROM customer_chunks")
        chunk_count = cursor.fetchone()[0]
        print(f"找到 {chunk_count} 条记录")

        print("步骤 2/5: 创建新表（带 CASCADE 约束）...")
        cursor.execute("""
            CREATE TABLE customer_chunks_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_profile_id INTEGER NOT NULL,
                chunk_text TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                chunk_metadata JSON,
                embedding BLOB,
                created_at DATETIME,
                FOREIGN KEY (customer_profile_id)
                    REFERENCES customer_profiles(id)
                    ON DELETE CASCADE
            )
        """)
        print("✅ 新表创建成功")

        print("步骤 3/5: 复制数据...")
        cursor.execute("""
            INSERT INTO customer_chunks_new
            SELECT * FROM customer_chunks
        """)
        copied_count = cursor.rowcount
        print(f"✅ 已复制 {copied_count} 条记录")

        print("步骤 4/5: 删除旧表...")
        cursor.execute("DROP TABLE customer_chunks")
        print("✅ 旧表已删除")

        print("步骤 5/5: 重命名新表...")
        cursor.execute("ALTER TABLE customer_chunks_new RENAME TO customer_chunks")
        print("✅ 表重命名完成")

        # 创建索引
        print("创建索引...")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_customer_chunks_customer_profile_id ON customer_chunks (customer_profile_id)")
        print("✅ 索引创建完成")

        conn.commit()

        print("=" * 60)
        print("✅ 外键约束修复完成！")
        print("=" * 60)
        print("现在删除客户时会自动删除关联的知识块")
        print("=" * 60)

    except Exception as e:
        conn.rollback()
        print(f"❌ 迁移失败: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
