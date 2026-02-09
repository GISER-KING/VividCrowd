"""
为面试会话表添加简历关联字段
"""
from sqlalchemy import text
from backend.core.database import digital_interviewer_sync_engine
from loguru import logger


def add_resume_field():
    """添加简历关联字段到interview_sessions表"""

    connection = digital_interviewer_sync_engine.connect()

    try:
        logger.info("开始添加resume_id字段到interview_sessions表...")

        # 添加resume_id字段
        connection.execute(text("""
            ALTER TABLE interview_sessions
            ADD COLUMN resume_id INTEGER
        """))
        connection.commit()
        logger.info("✅ resume_id字段添加成功")

    except Exception as e:
        if "duplicate column name" in str(e).lower():
            logger.info("⚠️ resume_id字段已存在，跳过")
        else:
            logger.error(f"添加字段失败: {e}")
            connection.rollback()
            raise
    finally:
        connection.close()


if __name__ == "__main__":
    add_resume_field()
    logger.info("✅ 迁移完成")
