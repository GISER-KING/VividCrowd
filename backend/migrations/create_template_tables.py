"""
创建评分模板和面试模板表
"""
from sqlalchemy import text
from backend.core.database import digital_interviewer_sync_engine
from loguru import logger


def create_template_tables():
    """创建模板表"""
    connection = digital_interviewer_sync_engine.connect()

    try:
        logger.info("开始创建模板表...")

        # 创建评分模板表
        logger.info("创建 scoring_templates 表...")
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS scoring_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                job_type VARCHAR(50),
                technical_weight INTEGER DEFAULT 25,
                communication_weight INTEGER DEFAULT 15,
                problem_solving_weight INTEGER DEFAULT 20,
                cultural_fit_weight INTEGER DEFAULT 10,
                innovation_weight INTEGER DEFAULT 10,
                teamwork_weight INTEGER DEFAULT 10,
                stress_handling_weight INTEGER DEFAULT 5,
                learning_ability_weight INTEGER DEFAULT 5,
                is_active BOOLEAN DEFAULT 1,
                is_default BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        connection.commit()
        logger.info("✅ scoring_templates 表创建成功")

    except Exception as e:
        logger.error(f"创建表失败: {e}")
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    create_template_tables()
