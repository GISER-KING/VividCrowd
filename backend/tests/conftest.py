"""
pytest 配置和 fixtures
"""
import sys
import os
import pytest
import pytest_asyncio

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select

from backend.core.database import Base, DATABASE_URL
from backend.models.db_models import CustomerServiceQA
from backend.apps.customer_service.services.qa_matcher import QAMatcher
from backend.apps.customer_service.services.orchestrator import CustomerServiceOrchestrator
from backend.core.config import settings


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def db_engine():
    """创建数据库引擎"""
    engine = create_async_engine(DATABASE_URL, echo=False)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine):
    """创建数据库会话"""
    async_session_maker = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture(scope="session")
async def qa_matcher(db_engine):
    """创建并初始化 QA Matcher"""
    async_session_maker = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_session_maker() as session:
        matcher = QAMatcher()
        await matcher.load_qa_data(session)
        yield matcher


@pytest_asyncio.fixture(scope="session")
async def orchestrator(db_engine):
    """创建并初始化 Orchestrator"""
    async_session_maker = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_session_maker() as session:
        orch = CustomerServiceOrchestrator(api_key=settings.DASHSCOPE_API_KEY)
        await orch.initialize(session)
        yield orch


@pytest_asyncio.fixture(scope="session")
async def qa_test_data(db_engine):
    """从数据库加载测试数据"""
    async_session_maker = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_session_maker() as session:
        result = await session.execute(select(CustomerServiceQA))
        qa_records = result.scalars().all()

        # 转换为测试数据格式
        test_cases = []
        for qa in qa_records:
            test_cases.append({
                'id': qa.id,
                'query': qa.typical_question,
                'topic_name': qa.topic_name,
                'expected_answer': qa.standard_script,
                'risk_notes': qa.risk_notes
            })

        yield test_cases
