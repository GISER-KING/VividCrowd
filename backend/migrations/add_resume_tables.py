"""
添加简历分析相关数据表
"""
from sqlalchemy import create_engine, text
from backend.core.database import get_digital_interviewer_db
from loguru import logger


def add_resume_tables():
    """添加简历相关的数据表"""

    db = next(get_digital_interviewer_db())

    try:
        logger.info("开始创建简历相关数据表...")

        # 1. 创建候选人简历表
        logger.info("创建 candidate_resumes 表...")
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS candidate_resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id VARCHAR(100),
                candidate_name VARCHAR(100),
                file_path VARCHAR(500) NOT NULL,
                file_type VARCHAR(20) NOT NULL,
                file_hash VARCHAR(64),
                parse_status VARCHAR(20) DEFAULT 'pending',
                parsed_data TEXT,
                quality_score INTEGER,
                completeness_score INTEGER,
                professionalism_score INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # 创建索引
        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_candidate_resumes_candidate_id
            ON candidate_resumes(candidate_id)
        """))

        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_candidate_resumes_candidate_name
            ON candidate_resumes(candidate_name)
        """))

        db.commit()
        logger.info("✅ candidate_resumes 表创建成功")

        # 2. 创建简历分析表
        logger.info("创建 resume_analysis 表...")
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS resume_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_id INTEGER NOT NULL UNIQUE,
                contact_info TEXT,
                education TEXT,
                work_experience TEXT,
                project_experience TEXT,
                skills TEXT,
                certifications TEXT,
                total_work_years REAL,
                education_level VARCHAR(50),
                major VARCHAR(100),
                skill_tags TEXT,
                industry_tags TEXT,
                position_tags TEXT,
                quality_issues TEXT,
                improvement_suggestions TEXT,
                risk_flags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (resume_id) REFERENCES candidate_resumes(id) ON DELETE CASCADE
            )
        """))

        db.commit()
        logger.info("✅ resume_analysis 表创建成功")

        # 3. 创建职位信息表
        logger.info("创建 job_positions 表...")
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS job_positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(100) NOT NULL,
                department VARCHAR(100),
                company VARCHAR(100),
                requirements TEXT,
                skills_required TEXT,
                skills_preferred TEXT,
                education_required VARCHAR(50),
                experience_years_min INTEGER,
                experience_years_max INTEGER,
                job_type VARCHAR(50),
                industry VARCHAR(100),
                location VARCHAR(100),
                salary_range VARCHAR(100),
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_job_positions_title
            ON job_positions(title)
        """))

        db.commit()
        logger.info("✅ job_positions 表创建成功")

        # 4. 创建简历职位匹配表
        logger.info("创建 resume_job_matches 表...")
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS resume_job_matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_id INTEGER NOT NULL,
                job_id INTEGER NOT NULL,
                match_score INTEGER NOT NULL,
                skill_match_score INTEGER,
                experience_match_score INTEGER,
                education_match_score INTEGER,
                matched_skills TEXT,
                missing_skills TEXT,
                match_details TEXT,
                priority VARCHAR(20),
                recommendations TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (resume_id) REFERENCES candidate_resumes(id) ON DELETE CASCADE,
                FOREIGN KEY (job_id) REFERENCES job_positions(id) ON DELETE CASCADE
            )
        """))

        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_resume_job_matches_resume_id
            ON resume_job_matches(resume_id)
        """))

        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_resume_job_matches_job_id
            ON resume_job_matches(job_id)
        """))

        db.commit()
        logger.info("✅ resume_job_matches 表创建成功")

    except Exception as e:
        logger.error(f"创建数据表失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    add_resume_tables()
    logger.info("✅ 所有简历相关数据表创建完成")
