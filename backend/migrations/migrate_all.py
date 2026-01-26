"""
一键完成数据库分离迁移

步骤:
1. 创建新的数据库表结构（celebrity.db 和 customerService.db）
2. 从旧的 app.db 迁移数据（如果存在）

运行方式:
python -m backend.migrations.migrate_all
"""
import asyncio
from loguru import logger

# 导入迁移脚本
from .add_celebrity_chunks import migrate as create_tables
from .migrate_data_from_old_db import migrate_from_old_db


async def migrate_all():
    """执行完整的数据库分离迁移"""
    logger.info("🚀 开始数据库分离迁移流程...")
    logger.info("")

    # 步骤 1: 创建新数据库表结构
    logger.info("📋 步骤 1/2: 创建数据库表结构")
    await create_tables()
    logger.info("")

    # 步骤 2: 迁移旧数据
    logger.info("📦 步骤 2/2: 迁移旧数据")
    await migrate_from_old_db()
    logger.info("")

    logger.info("=" * 60)
    logger.info("🎉 数据库分离完成！")
    logger.info("=" * 60)
    logger.info("新的数据库架构:")
    logger.info("  📁 backend/data/celebrity.db - 数字名人数据")
    logger.info("  📁 backend/data/customerService.db - 数字客服数据")
    logger.info("")
    logger.info("现在可以启动应用了:")
    logger.info("  uvicorn backend.main:app --reload")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(migrate_all())
