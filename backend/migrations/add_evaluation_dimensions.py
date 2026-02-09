"""
扩展面试评估维度 - 从4个维度扩展到8个维度
"""
from sqlalchemy import text
from backend.core.database import digital_interviewer_sync_engine
from loguru import logger


def add_evaluation_dimensions():
    """添加新的评估维度字段"""

    connection = digital_interviewer_sync_engine.connect()

    try:
        logger.info("开始添加新的评估维度字段...")

        # 添加4个新的评分字段
        new_columns = [
            ("innovation_score", "INTEGER"),
            ("teamwork_score", "INTEGER"),
            ("stress_handling_score", "INTEGER"),
            ("learning_ability_score", "INTEGER")
        ]

        for column_name, column_type in new_columns:
            try:
                logger.info(f"添加字段: {column_name}")
                connection.execute(text(f"""
                    ALTER TABLE interview_evaluations
                    ADD COLUMN {column_name} {column_type}
                """))
                connection.commit()
                logger.info(f"✅ {column_name} 字段添加成功")
            except Exception as e:
                if "duplicate column name" in str(e).lower():
                    logger.info(f"⚠️ {column_name} 字段已存在，跳过")
                else:
                    raise

        logger.info("✅ 所有新评估维度字段添加完成")

    except Exception as e:
        logger.error(f"添加字段失败: {e}")
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    add_evaluation_dimensions()
