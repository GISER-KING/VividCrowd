"""
数据库迁移脚本 - 为两个数据库创建表

功能:
1. celebrity.db - 创建名人相关表 (KnowledgeSource, CelebrityChunk)
2. customerService.db - 创建客服相关表 (CustomerServiceQA, CustomerServiceSession, CustomerServiceLog, CSVRegistry)

运行方式:
python -m backend.migrations.add_celebrity_chunks
"""
import asyncio
from loguru import logger
from sqlalchemy import select

from backend.core.database import (
    celebrity_engine,
    customer_service_engine,
    Base
)
from backend.models.db_models import (
    # Celebrity tables
    KnowledgeSource,
    CelebrityChunk,
    # Customer Service tables
    CustomerServiceQA,
    CustomerServiceSession,
    CustomerServiceLog,
    CSVRegistry
)


async def migrate_celebrity_db():
    """迁移名人数据库"""
    logger.info("开始迁移 celebrity.db...")

    async with celebrity_engine.begin() as conn:
        # 只创建名人相关的表
        await conn.run_sync(Base.metadata.create_all, tables=[
            KnowledgeSource.__table__,
            CelebrityChunk.__table__
        ])

    logger.info("✅ celebrity.db 迁移完成！")


async def migrate_customer_service_db():
    """迁移客服数据库"""
    logger.info("开始迁移 customerService.db...")

    async with customer_service_engine.begin() as conn:
        # 只创建客服相关的表
        await conn.run_sync(Base.metadata.create_all, tables=[
            CustomerServiceQA.__table__,
            CustomerServiceSession.__table__,
            CustomerServiceLog.__table__,
            CSVRegistry.__table__
        ])

    logger.info("✅ customerService.db 迁移完成！")


async def migrate():
    """执行所有数据库迁移"""
    logger.info("=" * 60)
    logger.info("开始数据库迁移 - 分离数据库架构")
    logger.info("=" * 60)

    # 并行执行两个数据库的迁移
    await asyncio.gather(
        migrate_celebrity_db(),
        migrate_customer_service_db()
    )

    logger.info("=" * 60)
    logger.info("✅ 所有数据库迁移完成！")
    logger.info("=" * 60)
    logger.info("数据库文件位置:")
    logger.info("  - backend/data/celebrity.db (数字名人)")
    logger.info("  - backend/data/customerService.db (数字客服)")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(migrate())
