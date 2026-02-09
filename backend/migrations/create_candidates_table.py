"""
创建候选人信息表
"""
from sqlalchemy import text
from backend.core.database import digital_interviewer_sync_engine
from loguru import logger


def create_candidates_table():
    """创建候选人表"""
    connection = digital_interviewer_sync_engine.connect()

    try:
        logger.info("开始创建candidates表...")

        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id VARCHAR(100) NOT NULL UNIQUE,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(200),
                phone VARCHAR(50),
                position VARCHAR(100),
                status VARCHAR(20) DEFAULT 'active',
                source VARCHAR(50),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        connection.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_candidates_candidate_id
            ON candidates(candidate_id)
        """))

        connection.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_candidates_name
            ON candidates(name)
        """))

        connection.commit()
        logger.info("✅ candidates表创建成功")

    except Exception as e:
        logger.error(f"创建表失败: {e}")
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    create_candidates_table()
