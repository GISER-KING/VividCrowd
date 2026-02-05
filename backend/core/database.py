from sqlalchemy.ext.asyncio.session import AsyncSession


from sqlalchemy.ext.asyncio.session import AsyncSession


import os
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# 数据库文件路径 - 存放在 backend/data/ 目录
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)  # 确保目录存在

# ==================== 数字名人数据库 ====================
CELEBRITY_DB_PATH = os.path.join(DATA_DIR, "celebrity.db")
CELEBRITY_DATABASE_URL = f"sqlite+aiosqlite:///{CELEBRITY_DB_PATH}"
CELEBRITY_SYNC_DATABASE_URL = f"sqlite:///{CELEBRITY_DB_PATH}"

# 异步引擎（用于异步操作）
celebrity_engine = create_async_engine(
    CELEBRITY_DATABASE_URL,
    echo=False,
    future=True
)

celebrity_async_session = async_sessionmaker[AsyncSession](
    celebrity_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 同步引擎（用于SessionManager等同步操作）
celebrity_sync_engine = create_engine(
    CELEBRITY_SYNC_DATABASE_URL,
    echo=False,
    future=True
)

celebrity_sync_session = sessionmaker(
    bind=celebrity_sync_engine,
    class_=Session,
    expire_on_commit=False
)

# ==================== 数字客服数据库 ====================
CUSTOMER_SERVICE_DB_PATH = os.path.join(DATA_DIR, "customerService.db")
CUSTOMER_SERVICE_DATABASE_URL = f"sqlite+aiosqlite:///{CUSTOMER_SERVICE_DB_PATH}"

customer_service_engine = create_async_engine(
    CUSTOMER_SERVICE_DATABASE_URL,
    echo=False,
    future=True
)

customer_service_async_session = async_sessionmaker[AsyncSession](
    customer_service_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# ==================== 数字客户数据库 ====================
DIGITAL_CUSTOMER_DB_PATH = os.path.join(DATA_DIR, "digital_customer.db")
DIGITAL_CUSTOMER_DATABASE_URL = f"sqlite+aiosqlite:///{DIGITAL_CUSTOMER_DB_PATH}"
DIGITAL_CUSTOMER_SYNC_DATABASE_URL = f"sqlite:///{DIGITAL_CUSTOMER_DB_PATH}"

# ==================== 数字面试官数据库 ====================
DIGITAL_INTERVIEWER_DB_PATH = os.path.join(DATA_DIR, "digital_interviewer.db")
DIGITAL_INTERVIEWER_DATABASE_URL = f"sqlite+aiosqlite:///{DIGITAL_INTERVIEWER_DB_PATH}"
DIGITAL_INTERVIEWER_SYNC_DATABASE_URL = f"sqlite:///{DIGITAL_INTERVIEWER_DB_PATH}"

# 异步引擎（用于异步操作）
digital_customer_engine = create_async_engine(
    DIGITAL_CUSTOMER_DATABASE_URL,
    echo=False,
    future=True
)

digital_customer_async_session = async_sessionmaker[AsyncSession](
    digital_customer_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 同步引擎（用于SessionManager等同步操作）
digital_customer_sync_engine = create_engine(
    DIGITAL_CUSTOMER_SYNC_DATABASE_URL,
    echo=False,
    future=True
)

digital_customer_sync_session = sessionmaker(
    bind=digital_customer_sync_engine,
    class_=Session,
    expire_on_commit=False
)

# 异步引擎（用于异步操作）
digital_interviewer_engine = create_async_engine(
    DIGITAL_INTERVIEWER_DATABASE_URL,
    echo=False,
    future=True
)

digital_interviewer_async_session = async_sessionmaker[AsyncSession](
    digital_interviewer_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 同步引擎（用于SessionManager等同步操作）
digital_interviewer_sync_engine = create_engine(
    DIGITAL_INTERVIEWER_SYNC_DATABASE_URL,
    echo=False,
    future=True
)

digital_interviewer_sync_session = sessionmaker(
    bind=digital_interviewer_sync_engine,
    class_=Session,
    expire_on_commit=False
)

# ==================== 兼容性保留 ====================
# 保留旧的变量名以兼容现有代码，默认指向客服数据库
engine = customer_service_engine
async_session = customer_service_async_session
DATABASE_URL = CUSTOMER_SERVICE_DATABASE_URL
DB_PATH = CUSTOMER_SERVICE_DB_PATH

# 声明基类
Base = declarative_base()


def get_celebrity_db():
    """
    获取Celebrity数据库会话（同步）
    用于依赖注入和SessionManager
    """
    db = celebrity_sync_session()
    try:
        yield db
    finally:
        db.close()


def get_digital_customer_db():
    """
    获取DigitalCustomer数据库会话（同步）
    用于依赖注入和SessionManager
    """
    db = digital_customer_sync_session()
    try:
        yield db
    finally:
        db.close()


def get_digital_interviewer_db():
    """
    获取DigitalInterviewer数据库会话（同步）
    用于依赖注入和SessionManager
    """
    db = digital_interviewer_sync_session()
    try:
        yield db
    finally:
        db.close()


def check_database_initialized(engine, table_name: str) -> bool:
    """
    检查数据库表是否已初始化

    Args:
        engine: SQLAlchemy引擎
        table_name: 表名

    Returns:
        bool: 表是否存在
    """
    from sqlalchemy import inspect
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


async def init_db():
    """
    初始化数据库，创建所有表

    注意：此函数为兼容性保留，实际应使用迁移脚本：
    python -m backend.migrations.migrate_all
    """
    from loguru import logger
    from backend.models.db_models import (
        KnowledgeSource,
        CelebrityChunk,
        CustomerServiceQA,
        CustomerServiceSession,
        CustomerServiceLog,
        CSVRegistry,
        CustomerProfile,
        CustomerChunk,
        ChatSession,
        ChatMessage,
        SalesKnowledge,
        TrainingSession,
        ConversationRound,
        StageEvaluation,
        FinalEvaluation,
        InterviewerProfile,
        InterviewerProfileRegistry,
        DigitalHuman,
        InterviewSession,
        InterviewRound,
        InterviewEvaluation,
        InterviewKnowledge,
        InterviewExperienceSet
    )

    # 初始化名人数据库
    if check_database_initialized(celebrity_sync_engine, 'knowledge_sources'):
        logger.info("📚 数字名人数据库已存在，跳过初始化")
    else:
        logger.info("🔧 初始化数字名人数据库...")
        async with celebrity_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all, tables=[
                KnowledgeSource.__table__,
                CelebrityChunk.__table__,
                ChatSession.__table__,
                ChatMessage.__table__
            ])
        logger.info("✅ 数字名人数据库初始化完成")

    # 初始化客服数据库
    if check_database_initialized(celebrity_sync_engine, 'customer_service_qa'):
        logger.info("📞 数字客服数据库已存在，跳过初始化")
    else:
        logger.info("🔧 初始化数字客服数据库...")
        async with customer_service_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all, tables=[
                CustomerServiceQA.__table__,
                CustomerServiceSession.__table__,
                CustomerServiceLog.__table__,
                CSVRegistry.__table__
            ])
        logger.info("✅ 数字客服数据库初始化完成")

    # 初始化客户数据库
    if check_database_initialized(digital_customer_sync_engine, 'customer_profiles'):
        logger.info("👥 数字客户数据库已存在，跳过初始化")
    else:
        logger.info("🔧 初始化数字客户数据库...")
        Base.metadata.create_all(
            bind=digital_customer_sync_engine,
            tables=[
                CustomerProfile.__table__,
                CustomerChunk.__table__,
                ChatSession.__table__,
                ChatMessage.__table__,
                SalesKnowledge.__table__,
                TrainingSession.__table__,
                ConversationRound.__table__,
                StageEvaluation.__table__,
                FinalEvaluation.__table__
            ])
        logger.info("✅ 数字客户数据库初始化完成")

    # 初始化面试官数据库
    if check_database_initialized(digital_interviewer_sync_engine, 'interviewer_profiles'):
        logger.info("💼 数字面试官数据库已存在，跳过初始化")
    else:
        logger.info("🔧 初始化数字面试官数据库...")
        Base.metadata.create_all(
            bind=digital_interviewer_sync_engine,
            tables=[
                InterviewerProfile.__table__,
                InterviewerProfileRegistry.__table__,
                DigitalHuman.__table__,
                InterviewSession.__table__,
                InterviewRound.__table__,
                InterviewEvaluation.__table__,
                InterviewKnowledge.__table__,
                InterviewExperienceSet.__table__
            ])
        logger.info("✅ 数字面试官数据库初始化完成")