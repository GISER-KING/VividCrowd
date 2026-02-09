"""
为面试会话表添加评分模板关联字段
"""
from sqlalchemy import text
from backend.core.database import digital_interviewer_sync_engine
from loguru import logger


def add_scoring_template_field():
    """添加scoring_template_id字段到interview_sessions表"""

    connection = digital_interviewer_sync_engine.connect()

    try:
        logger.info("开始添加scoring_template_id字段...")

        connection.execute(text("""
            ALTER TABLE interview_sessions
            ADD COLUMN scoring_template_id INTEGER
        """))
        connection.commit()
        logger.info("✅ scoring_template_id字段添加成功")

    except Exception as e:
        if "duplicate column name" in str(e).lower():
            logger.info("⚠️ scoring_template_id字段已存在，跳过")
        else:
            logger.error(f"添加字段失败: {e}")
            connection.rollback()
            raise
    finally:
        connection.close()


if __name__ == "__main__":
    add_scoring_template_field()
    logger.info("✅ 迁移完成")
