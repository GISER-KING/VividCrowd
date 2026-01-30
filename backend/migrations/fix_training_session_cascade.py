"""
数据迁移: 修复 TrainingSession 表的外键约束，添加级联删除

问题: training_sessions 表的 customer_profile_id 外键缺少 CASCADE 删除
导致: 删除有培训记录的客户时失败

解决: 重建表并添加 CASCADE 约束

运行方式:
python -m backend.migrations.fix_training_session_cascade
"""
import sqlite3
from loguru import logger
from backend.core.database import DIGITAL_CUSTOMER_DB_PATH


def migrate():
    """修复 TrainingSession 外键约束"""
    logger.info("=" * 60)
    logger.info("开始修复 TrainingSession 表外键约束...")
    logger.info("=" * 60)

    conn = sqlite3.connect(DIGITAL_CUSTOMER_DB_PATH)
    cursor = conn.cursor()

    try:
        # 检查表是否存在
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='training_sessions'
        """)
        if not cursor.fetchone():
            logger.info("⚠ training_sessions 表不存在，跳过迁移")
            return

        logger.info("步骤 1/4: 创建新表（带 CASCADE 约束）...")
        cursor.execute("""
            CREATE TABLE training_sessions_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id VARCHAR(64) UNIQUE NOT NULL,
                trainee_id VARCHAR(100),
                trainee_name VARCHAR(100),
                customer_profile_id INTEGER NOT NULL,
                current_stage INTEGER DEFAULT 1,
                current_round INTEGER DEFAULT 0,
                total_rounds INTEGER DEFAULT 0,
                status VARCHAR(20) DEFAULT 'active',
                created_at DATETIME,
                updated_at DATETIME,
                FOREIGN KEY (customer_profile_id)
                    REFERENCES customer_profiles(id)
                    ON DELETE CASCADE
            )
        """)
        logger.info("✅ 新表创建成功")

        logger.info("步骤 2/4: 复制数据...")
        cursor.execute("""
            INSERT INTO training_sessions_new
            SELECT * FROM training_sessions
        """)
        copied_count = cursor.rowcount
        logger.info(f"✅ 已复制 {copied_count} 条记录")

        logger.info("步骤 3/4: 删除旧表...")
        cursor.execute("DROP TABLE training_sessions")
        logger.info("✅ 旧表已删除")

        logger.info("步骤 4/4: 重命名新表...")
        cursor.execute("ALTER TABLE training_sessions_new RENAME TO training_sessions")
        logger.info("✅ 表重命名完成")

        # 创建索引
        logger.info("创建索引...")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_training_sessions_session_id ON training_sessions (session_id)")
        logger.info("✅ 索引创建完成")

        conn.commit()

        logger.info("=" * 60)
        logger.info("✅ 外键约束修复完成！")
        logger.info("=" * 60)
        logger.info("现在删除客户时会自动删除关联的培训记录")
        logger.info("=" * 60)

    except Exception as e:
        conn.rollback()
        logger.error(f"❌ 迁移失败: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
