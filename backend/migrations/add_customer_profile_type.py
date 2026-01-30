"""
数据迁移: 为 CustomerProfile 表添加 profile_type 字段

功能:
1. 添加 profile_type 列（客户画像类型）
2. 将现有 name 数据迁移到 profile_type
3. 清空 name 字段（用于存储真实客户姓名）

运行方式:
python -m backend.migrations.add_customer_profile_type
"""
import sqlite3
from loguru import logger
from backend.core.database import DIGITAL_CUSTOMER_DB_PATH


def migrate():
    """执行数据库迁移"""
    logger.info("=" * 60)
    logger.info("开始 CustomerProfile 表结构迁移...")
    logger.info("=" * 60)

    conn = sqlite3.connect(DIGITAL_CUSTOMER_DB_PATH)
    cursor = conn.cursor()

    try:
        # 检查 profile_type 列是否已存在
        cursor.execute("PRAGMA table_info(customer_profiles)")
        columns = {column[1]: column for column in cursor.fetchall()}

        profile_type_exists = 'profile_type' in columns
        name_is_nullable = columns.get('name', [None, None, None, 0])[3] == 0  # notnull=0 means nullable

        if profile_type_exists and name_is_nullable:
            logger.warning("⚠ 迁移已完成，无需重复执行")
            return

        if not profile_type_exists:
            logger.info("步骤 1/3: 添加 profile_type 列...")
            cursor.execute("""
                ALTER TABLE customer_profiles
                ADD COLUMN profile_type VARCHAR(100)
            """)
            logger.info("✅ profile_type 列添加成功")
        else:
            logger.info("步骤 1/3: profile_type 列已存在，跳过添加")

        logger.info("步骤 2/3: 迁移现有数据 (name -> profile_type)...")
        cursor.execute("""
            UPDATE customer_profiles
            SET profile_type = name
            WHERE profile_type IS NULL
        """)
        migrated_count = cursor.rowcount
        logger.info(f"✅ 已迁移 {migrated_count} 条记录")

        logger.info("步骤 3/3: 移除 name 列的 NOT NULL 约束...")
        logger.info("注意: SQLite 不支持直接修改列约束，需要重建表")

        # 获取表结构
        cursor.execute("PRAGMA table_info(customer_profiles)")
        columns = cursor.fetchall()

        # 创建新表（name 列为 nullable）
        logger.info("  - 创建临时表...")
        cursor.execute("""
            CREATE TABLE customer_profiles_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100),
                profile_type VARCHAR(100) NOT NULL,
                age_range VARCHAR(50),
                gender VARCHAR(20),
                occupation VARCHAR(100),
                industry VARCHAR(100),
                personality_traits TEXT,
                communication_style TEXT,
                pain_points TEXT,
                needs TEXT,
                objections TEXT,
                system_prompt TEXT,
                raw_content TEXT,
                source_file_path VARCHAR(500),
                created_at DATETIME,
                updated_at DATETIME
            )
        """)

        # 复制数据
        logger.info("  - 复制数据到新表...")
        cursor.execute("""
            INSERT INTO customer_profiles_new
            SELECT id, name, profile_type, age_range, gender, occupation, industry,
                   personality_traits, communication_style, pain_points, needs, objections,
                   system_prompt, raw_content, source_file_path, created_at, updated_at
            FROM customer_profiles
        """)

        # 删除旧表
        logger.info("  - 删除旧表...")
        cursor.execute("DROP TABLE customer_profiles")

        # 重命名新表
        logger.info("  - 重命名新表...")
        cursor.execute("ALTER TABLE customer_profiles_new RENAME TO customer_profiles")

        # 创建索引
        logger.info("  - 创建索引...")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_customer_profiles_name ON customer_profiles (name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_customer_profiles_profile_type ON customer_profiles (profile_type)")

        logger.info("✅ 表结构更新完成")

        conn.commit()

        logger.info("=" * 60)
        logger.info("✅ 数据迁移完成！")
        logger.info("=" * 60)
        logger.info("变更说明:")
        logger.info("  - name: 现在用于存储真实客户姓名（可选，现有数据保留画像类型）")
        logger.info("  - profile_type: 存储客户画像类型（必填）")
        logger.info("  - 现有客户: name 和 profile_type 都是画像类型，显示正常")
        logger.info("  - 新上传客户: name 为真实姓名（如有），profile_type 为画像类型")
        logger.info("=" * 60)

    except Exception as e:
        conn.rollback()
        logger.error(f"❌ 迁移失败: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
