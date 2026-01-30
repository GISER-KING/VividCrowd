"""
数据迁移: 重构数字客户数据库结构

变更内容:
1. 添加 CustomerProfileRegistry 表（文件注册表）
2. 移除所有表的 CASCADE 删除约束
3. 为 CustomerChunk 添加冗余字段（customer_name, customer_profile_type）
4. 为 TrainingSession 添加冗余字段（customer_name, customer_profile_type, customer_occupation, customer_industry, total_rounds, created_at, updated_at）
5. 填充现有数据的冗余字段

运行方式:
python backend/migrations/restructure_digital_customer_db.py
"""
import sqlite3
import os

# 直接构建数据库路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(BACKEND_DIR, "data")
DIGITAL_CUSTOMER_DB_PATH = os.path.join(DATA_DIR, "digital_customer.db")


def migrate():
    """重构数字客户数据库"""
    print("=" * 60)
    print("开始重构数字客户数据库...")
    print("=" * 60)
    print(f"数据库路径: {DIGITAL_CUSTOMER_DB_PATH}")

    if not os.path.exists(DIGITAL_CUSTOMER_DB_PATH):
        print(f"❌ 数据库文件不存在: {DIGITAL_CUSTOMER_DB_PATH}")
        return

    conn = sqlite3.connect(DIGITAL_CUSTOMER_DB_PATH)
    cursor = conn.cursor()

    try:
        # ==================== 步骤 1: 创建 CustomerProfileRegistry 表 ====================
        print("\n步骤 1/5: 创建 CustomerProfileRegistry 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_profile_registry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename VARCHAR(255) UNIQUE NOT NULL,
                file_hash VARCHAR(64) NOT NULL,
                customer_profile_id INTEGER,
                customer_name VARCHAR(100),
                customer_profile_type VARCHAR(100),
                status VARCHAR(20) DEFAULT 'success',
                imported_at DATETIME
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_customer_profile_registry_filename ON customer_profile_registry (filename)")
        print("✅ CustomerProfileRegistry 表创建完成")

        # ==================== 步骤 2: 重建 CustomerChunk 表 ====================
        print("\n步骤 2/5: 重建 CustomerChunk 表（添加冗余字段，移除 CASCADE）...")

        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='customer_chunks'")
        if cursor.fetchone():
            cursor.execute("SELECT COUNT(*) FROM customer_chunks")
            chunk_count = cursor.fetchone()[0]
            print(f"找到 {chunk_count} 条 chunk 记录")

            # 创建新表
            cursor.execute("""
                CREATE TABLE customer_chunks_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_profile_id INTEGER NOT NULL,
                    customer_name VARCHAR(100),
                    customer_profile_type VARCHAR(100),
                    chunk_text TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    chunk_metadata JSON,
                    embedding BLOB,
                    created_at DATETIME,
                    FOREIGN KEY (customer_profile_id) REFERENCES customer_profiles(id)
                )
            """)

            # 复制数据并填充冗余字段
            cursor.execute("""
                INSERT INTO customer_chunks_new
                    (id, customer_profile_id, customer_name, customer_profile_type,
                     chunk_text, chunk_index, chunk_metadata, embedding, created_at)
                SELECT
                    c.id, c.customer_profile_id,
                    p.name, p.profile_type,
                    c.chunk_text, c.chunk_index, c.chunk_metadata, c.embedding, c.created_at
                FROM customer_chunks c
                LEFT JOIN customer_profiles p ON c.customer_profile_id = p.id
            """)

            # 删除旧表，重命名新表
            cursor.execute("DROP TABLE customer_chunks")
            cursor.execute("ALTER TABLE customer_chunks_new RENAME TO customer_chunks")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_customer_chunks_customer_profile_id ON customer_chunks (customer_profile_id)")
            print("✅ CustomerChunk 表重建完成")
        else:
            print("⚠ customer_chunks 表不存在，跳过")

        # ==================== 步骤 3: 重建 TrainingSession 表 ====================
        print("\n步骤 3/5: 重建 TrainingSession 表（添加冗余字段，移除 CASCADE）...")

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='training_sessions'")
        if cursor.fetchone():
            cursor.execute("SELECT COUNT(*) FROM training_sessions")
            session_count = cursor.fetchone()[0]
            print(f"找到 {session_count} 条培训会话记录")

            # 创建新表
            cursor.execute("""
                CREATE TABLE training_sessions_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id VARCHAR(64) UNIQUE NOT NULL,
                    trainee_id VARCHAR(100),
                    trainee_name VARCHAR(100),
                    customer_profile_id INTEGER NOT NULL,
                    customer_name VARCHAR(100),
                    customer_profile_type VARCHAR(100),
                    customer_occupation VARCHAR(100),
                    customer_industry VARCHAR(100),
                    current_stage INTEGER DEFAULT 1,
                    current_round INTEGER DEFAULT 0,
                    total_rounds INTEGER DEFAULT 0,
                    status VARCHAR(20) DEFAULT 'in_progress',
                    started_at DATETIME,
                    completed_at DATETIME,
                    duration_seconds INTEGER,
                    created_at DATETIME,
                    updated_at DATETIME,
                    FOREIGN KEY (customer_profile_id) REFERENCES customer_profiles(id)
                )
            """)

            # 复制数据并填充冗余字段
            cursor.execute("""
                INSERT INTO training_sessions_new
                    (id, session_id, trainee_id, trainee_name, customer_profile_id,
                     customer_name, customer_profile_type, customer_occupation, customer_industry,
                     current_stage, current_round, total_rounds, status,
                     started_at, completed_at, duration_seconds, created_at, updated_at)
                SELECT
                    t.id, t.session_id, t.trainee_id, t.trainee_name, t.customer_profile_id,
                    p.name, p.profile_type, p.occupation, p.industry,
                    t.current_stage, t.current_round,
                    COALESCE(t.total_rounds, 0),
                    t.status,
                    t.started_at, t.completed_at, t.duration_seconds,
                    t.started_at, t.started_at
                FROM training_sessions t
                LEFT JOIN customer_profiles p ON t.customer_profile_id = p.id
            """)

            # 删除旧表，重命名新表
            cursor.execute("DROP TABLE training_sessions")
            cursor.execute("ALTER TABLE training_sessions_new RENAME TO training_sessions")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_training_sessions_session_id ON training_sessions (session_id)")
            print("✅ TrainingSession 表重建完成")
        else:
            print("⚠ training_sessions 表不存在，跳过")

        # ==================== 步骤 4: 重建 ConversationRound 表 ====================
        print("\n步骤 4/5: 重建 ConversationRound 表（移除 CASCADE）...")

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='conversation_rounds'")
        if cursor.fetchone():
            cursor.execute("SELECT COUNT(*) FROM conversation_rounds")
            round_count = cursor.fetchone()[0]
            print(f"找到 {round_count} 条对话轮次记录")

            cursor.execute("""
                CREATE TABLE conversation_rounds_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    round_number INTEGER NOT NULL,
                    stage INTEGER NOT NULL,
                    trainee_message TEXT NOT NULL,
                    customer_response TEXT NOT NULL,
                    detected_quality VARCHAR(50),
                    analysis_data JSON,
                    timestamp DATETIME,
                    FOREIGN KEY (session_id) REFERENCES training_sessions(id)
                )
            """)

            cursor.execute("INSERT INTO conversation_rounds_new SELECT * FROM conversation_rounds")
            cursor.execute("DROP TABLE conversation_rounds")
            cursor.execute("ALTER TABLE conversation_rounds_new RENAME TO conversation_rounds")
            print("✅ ConversationRound 表重建完成")
        else:
            print("⚠ conversation_rounds 表不存在，跳过")

        # ==================== 步骤 5: 重建 StageEvaluation 和 FinalEvaluation 表 ====================
        print("\n步骤 5/5: 重建评价表（移除 CASCADE）...")

        # StageEvaluation
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stage_evaluations'")
        if cursor.fetchone():
            cursor.execute("""
                CREATE TABLE stage_evaluations_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    stage_number INTEGER NOT NULL,
                    stage_name VARCHAR(100),
                    task_completed BOOLEAN DEFAULT 0,
                    completion_quality VARCHAR(50),
                    strengths JSON,
                    weaknesses JSON,
                    suggestions JSON,
                    score INTEGER,
                    started_at DATETIME,
                    completed_at DATETIME,
                    rounds_used INTEGER,
                    FOREIGN KEY (session_id) REFERENCES training_sessions(id)
                )
            """)
            cursor.execute("INSERT INTO stage_evaluations_new SELECT * FROM stage_evaluations")
            cursor.execute("DROP TABLE stage_evaluations")
            cursor.execute("ALTER TABLE stage_evaluations_new RENAME TO stage_evaluations")
            print("✅ StageEvaluation 表重建完成")

        # FinalEvaluation
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='final_evaluations'")
        if cursor.fetchone():
            cursor.execute("""
                CREATE TABLE final_evaluations_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER UNIQUE NOT NULL,
                    trust_building_score INTEGER,
                    needs_diagnosis_score INTEGER,
                    value_presentation_score INTEGER,
                    objection_handling_score INTEGER,
                    progress_management_score INTEGER,
                    total_score INTEGER,
                    performance_level VARCHAR(20),
                    overall_strengths JSON,
                    overall_weaknesses JSON,
                    key_improvements JSON,
                    uncompleted_tasks JSON,
                    detailed_report TEXT,
                    created_at DATETIME,
                    FOREIGN KEY (session_id) REFERENCES training_sessions(id)
                )
            """)
            cursor.execute("INSERT INTO final_evaluations_new SELECT * FROM final_evaluations")
            cursor.execute("DROP TABLE final_evaluations")
            cursor.execute("ALTER TABLE final_evaluations_new RENAME TO final_evaluations")
            print("✅ FinalEvaluation 表重建完成")

        conn.commit()

        print("\n" + "=" * 60)
        print("✅ 数据库重构完成！")
        print("=" * 60)
        print("变更总结:")
        print("1. ✅ 添加了 CustomerProfileRegistry 表")
        print("2. ✅ 移除了所有 CASCADE 删除约束")
        print("3. ✅ 为 CustomerChunk 添加了冗余字段")
        print("4. ✅ 为 TrainingSession 添加了冗余字段")
        print("5. ✅ 填充了现有数据的冗余字段")
        print("=" * 60)

    except Exception as e:
        conn.rollback()
        print(f"\n❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
