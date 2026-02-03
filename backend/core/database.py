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


async def init_db():
    """
    初始化数据库，创建所有表

    注意：此函数为兼容性保留，实际应使用迁移脚本：
    python -m backend.migrations.migrate_all
    """
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
        FinalEvaluation
    )

    # 初始化名人数据库
    async with celebrity_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, tables=[
            KnowledgeSource.__table__,
            CelebrityChunk.__table__,
            ChatSession.__table__,
            ChatMessage.__table__
        ])

    # 初始化客服数据库
    async with customer_service_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, tables=[
            CustomerServiceQA.__table__,
            CustomerServiceSession.__table__,
            CustomerServiceLog.__table__,
            CSVRegistry.__table__
        ])

    # 初始化客户数据库
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