"""
数据迁移工具 - 从旧的 app.db 迁移数据到新的分离数据库

功能:
1. 从 app.db 读取所有数据
2. 将名人数据迁移到 celebrity.db
3. 将客服数据迁移到 customerService.db

运行方式:
python -m backend.migrations.migrate_data_from_old_db
"""
import asyncio
import os
import shutil
from loguru import logger
from sqlalchemy import select, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from backend.core.database import (
    celebrity_async_session,
    customer_service_async_session,
    DATA_DIR
)
from backend.models.db_models import (
    KnowledgeSource,
    CelebrityChunk,
    CustomerServiceQA,
    CustomerServiceSession,
    CustomerServiceLog,
    CSVRegistry
)


async def migrate_from_old_db():
    """从旧的 app.db 迁移数据"""

    old_db_path = os.path.join(DATA_DIR, "app.db")

    # 检查旧数据库是否存在
    if not os.path.exists(old_db_path):
        logger.warning(f"未找到旧数据库文件: {old_db_path}")
        logger.info("如果这是首次运行，请忽略此警告")
        return

    logger.info("=" * 60)
    logger.info(f"发现旧数据库: {old_db_path}")
    logger.info("开始数据迁移...")
    logger.info("=" * 60)

    # 创建旧数据库连接
    old_db_url = f"sqlite+aiosqlite:///{old_db_path}"
    old_engine = create_async_engine(old_db_url, echo=False)
    old_session_maker = async_sessionmaker(old_engine, class_=AsyncSession, expire_on_commit=False)

    try:
        # 迁移名人数据
        await migrate_celebrity_data(old_session_maker)

        # 迁移客服数据
        await migrate_customer_service_data(old_session_maker)

        # 备份旧数据库
        backup_path = old_db_path + ".backup"
        shutil.copy2(old_db_path, backup_path)
        logger.info(f"✅ 旧数据库已备份到: {backup_path}")

        logger.info("=" * 60)
        logger.info("✅ 数据迁移完成！")
        logger.info("=" * 60)
        logger.info("你可以:")
        logger.info(f"  1. 删除旧数据库: {old_db_path}")
        logger.info(f"  2. 或保留备份: {backup_path}")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"❌ 数据迁移失败: {e}")
        raise
    finally:
        await old_engine.dispose()


async def migrate_celebrity_data(old_session_maker):
    """迁移名人相关数据"""
    logger.info("迁移名人数据到 celebrity.db...")

    async with old_session_maker() as old_db:
        async with celebrity_async_session() as new_db:
            # 迁移 KnowledgeSource
            result = await old_db.execute(select(KnowledgeSource))
            knowledge_sources = result.scalars().all()

            if knowledge_sources:
                logger.info(f"  - 发现 {len(knowledge_sources)} 条 KnowledgeSource 记录")
                for ks in knowledge_sources:
                    # 创建新记录（不包含 id，让数据库自动生成）
                    new_ks = KnowledgeSource(
                        name=ks.name,
                        source_type=ks.source_type,
                        author=ks.author,
                        birth_year=ks.birth_year,
                        death_year=ks.death_year,
                        nationality=ks.nationality,
                        occupation=ks.occupation,
                        biography=ks.biography,
                        famous_works=ks.famous_works,
                        famous_quotes=ks.famous_quotes,
                        personality_traits=ks.personality_traits,
                        speech_style=ks.speech_style,
                        system_prompt=ks.system_prompt,
                        knowledge_base=ks.knowledge_base,
                        raw_content=ks.raw_content,
                        source_pdf_path=ks.source_pdf_path,
                        created_at=ks.created_at,
                        updated_at=ks.updated_at
                    )
                    new_db.add(new_ks)

                await new_db.flush()  # 生成新 ID
                logger.info(f"  ✅ 已迁移 {len(knowledge_sources)} 条 KnowledgeSource")

                # 迁移 CelebrityChunk（如果存在）
                try:
                    chunk_result = await old_db.execute(select(CelebrityChunk))
                    chunks = chunk_result.scalars().all()

                    if chunks:
                        logger.info(f"  - 发现 {len(chunks)} 条 CelebrityChunk 记录")

                        # 创建 ID 映射 (old_id -> new_id)
                        id_mapping = {}
                        new_sources = (await new_db.execute(select(KnowledgeSource))).scalars().all()
                        for old_ks, new_ks in zip(knowledge_sources, new_sources):
                            id_mapping[old_ks.id] = new_ks.id

                        for chunk in chunks:
                            new_chunk = CelebrityChunk(
                                knowledge_source_id=id_mapping.get(chunk.knowledge_source_id),
                                chunk_text=chunk.chunk_text,
                                chunk_index=chunk.chunk_index,
                                chunk_metadata=chunk.chunk_metadata,
                                embedding=chunk.embedding,
                                created_at=chunk.created_at
                            )
                            new_db.add(new_chunk)

                        logger.info(f"  ✅ 已迁移 {len(chunks)} 条 CelebrityChunk")
                except Exception as e:
                    logger.warning(f"  ⚠ CelebrityChunk 表不存在或迁移失败: {e}")

            else:
                logger.info("  - 未发现名人数据")

            await new_db.commit()


async def migrate_customer_service_data(old_session_maker):
    """迁移客服相关数据"""
    logger.info("迁移客服数据到 customerService.db...")

    async with old_session_maker() as old_db:
        async with customer_service_async_session() as new_db:
            # 迁移 CustomerServiceQA
            try:
                result = await old_db.execute(select(CustomerServiceQA))
                qa_records = result.scalars().all()

                if qa_records:
                    logger.info(f"  - 发现 {len(qa_records)} 条 CustomerServiceQA 记录")
                    for qa in qa_records:
                        new_qa = CustomerServiceQA(
                            question_count=qa.question_count,
                            topic_name=qa.topic_name,
                            typical_question=qa.typical_question,
                            standard_script=qa.standard_script,
                            risk_notes=qa.risk_notes,
                            keywords=qa.keywords,
                            embedding=qa.embedding,
                            created_at=qa.created_at
                        )
                        new_db.add(new_qa)
                    logger.info(f"  ✅ 已迁移 {len(qa_records)} 条 CustomerServiceQA")
            except Exception as e:
                logger.warning(f"  ⚠ CustomerServiceQA 迁移失败: {e}")

            # 迁移 CustomerServiceSession
            try:
                result = await old_db.execute(select(CustomerServiceSession))
                sessions = result.scalars().all()

                if sessions:
                    logger.info(f"  - 发现 {len(sessions)} 条 CustomerServiceSession 记录")
                    for session in sessions:
                        new_session = CustomerServiceSession(
                            session_id=session.session_id,
                            start_time=session.start_time,
                            message_count=session.message_count,
                            avg_confidence=session.avg_confidence,
                            transfer_to_human=session.transfer_to_human,
                            user_rating=session.user_rating
                        )
                        new_db.add(new_session)
                    logger.info(f"  ✅ 已迁移 {len(sessions)} 条 CustomerServiceSession")
            except Exception as e:
                logger.warning(f"  ⚠ CustomerServiceSession 迁移失败: {e}")

            # 迁移 CustomerServiceLog
            try:
                result = await old_db.execute(select(CustomerServiceLog))
                logs = result.scalars().all()

                if logs:
                    logger.info(f"  - 发现 {len(logs)} 条 CustomerServiceLog 记录")
                    for log in logs:
                        new_log = CustomerServiceLog(
                            session_id=log.session_id,
                            user_query=log.user_query,
                            bot_response=log.bot_response,
                            matched_qa_id=log.matched_qa_id,
                            match_type=log.match_type,
                            confidence_score=log.confidence_score,
                            response_time_ms=log.response_time_ms,
                            timestamp=log.timestamp
                        )
                        new_db.add(new_log)
                    logger.info(f"  ✅ 已迁移 {len(logs)} 条 CustomerServiceLog")
            except Exception as e:
                logger.warning(f"  ⚠ CustomerServiceLog 迁移失败: {e}")

            # 迁移 CSVRegistry
            try:
                result = await old_db.execute(select(CSVRegistry))
                csv_records = result.scalars().all()

                if csv_records:
                    logger.info(f"  - 发现 {len(csv_records)} 条 CSVRegistry 记录")
                    for csv_rec in csv_records:
                        new_csv = CSVRegistry(
                            filename=csv_rec.filename,
                            file_hash=csv_rec.file_hash,
                            record_count=csv_rec.record_count,
                            status=csv_rec.status,
                            imported_at=csv_rec.imported_at
                        )
                        new_db.add(new_csv)
                    logger.info(f"  ✅ 已迁移 {len(csv_records)} 条 CSVRegistry")
            except Exception as e:
                logger.warning(f"  ⚠ CSVRegistry 迁移失败: {e}")

            await new_db.commit()


if __name__ == "__main__":
    asyncio.run(migrate_from_old_db())
