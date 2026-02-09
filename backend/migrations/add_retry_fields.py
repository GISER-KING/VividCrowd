"""
为面试轮次表添加重录相关字段
"""
from sqlalchemy import text
from backend.core.database import digital_interviewer_sync_engine
from loguru import logger


def add_retry_fields():
    """添加重录字段到interview_rounds表"""
    connection = digital_interviewer_sync_engine.connect()

    try:
        logger.info("开始添加重录相关字段...")

        # 添加retry_count字段
        try:
            connection.execute(text("""
                ALTER TABLE interview_rounds
                ADD COLUMN retry_count INTEGER DEFAULT 0
            """))
            connection.commit()
            logger.info("✅ retry_count字段添加成功")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                logger.info("⚠️ retry_count字段已存在，跳过")
            else:
                raise

        # 添加retry_history字段
        try:
            connection.execute(text("""
                ALTER TABLE interview_rounds
                ADD COLUMN retry_history TEXT
            """))
            connection.commit()
            logger.info("✅ retry_history字段添加成功")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                logger.info("⚠️ retry_history字段已存在，跳过")
            else:
                raise

        logger.info("✅ 所有重录字段添加完成")

    except Exception as e:
        logger.error(f"添加字段失败: {e}")
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    add_retry_fields()
