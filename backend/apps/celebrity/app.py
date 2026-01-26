"""
数字分身子应用 - 名人数字分身功能
"""
import os
import json
import shutil
import asyncio
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form, HTTPException
from sqlalchemy import select
from loguru import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from backend.core.database import celebrity_async_session, get_celebrity_db, celebrity_sync_engine
from backend.models.db_models import KnowledgeSource, CelebrityChunk, ChatSession, ChatMessage, Base
from backend.models.schemas import CelebrityResponse
from .services.celebrity_orchestrator import CelebrityOrchestratorService
from .services.session_manager import CelebritySessionManager
from .services.pdf_parser import pdf_parser_service
from .services.chunking_service import chunking_service
from backend.apps.customer_service.services.embedding_service import embedding_service

# 创建子应用
celebrity_app = FastAPI(title="VividCrowd Celebrity API", version="1.0.0")

# 创建定时任务调度器
scheduler = AsyncIOScheduler()

# PDF 上传目录
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@celebrity_app.get("/", response_model=List[CelebrityResponse])
async def get_celebrities():
    """获取所有名人列表"""
    async with celebrity_async_session() as session:
        result = await session.execute(select(KnowledgeSource))
        celebrities = result.scalars().all()
        return [CelebrityResponse.model_validate(c) for c in celebrities]


@celebrity_app.get("/{celebrity_id}", response_model=CelebrityResponse)
async def get_celebrity(celebrity_id: int):
    """获取名人详情"""
    async with celebrity_async_session() as session:
        result = await session.execute(
            select(KnowledgeSource).where(KnowledgeSource.id == celebrity_id)
        )
        celebrity = result.scalar_one_or_none()
        if not celebrity:
            raise HTTPException(status_code=404, detail="名人不存在")
        return CelebrityResponse.model_validate(celebrity)


@celebrity_app.post("/upload", response_model=CelebrityResponse)
async def upload_celebrity(
    file: UploadFile = File(...),
    source_type: str = Form("person")
):
    """上传文档（PDF或Markdown）并解析创建名人"""
    # 检查文件类型
    if not (file.filename.endswith(".pdf") or file.filename.endswith(".md")):
        raise HTTPException(status_code=400, detail="只支持 PDF 或 Markdown 文件")

    # 保存上传的文件
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        # 根据文件类型提取文本
        raw_text = pdf_parser_service.extract_text_from_file(file_path)

        # 使用 LLM 解析结构化信息
        parsed_info = await pdf_parser_service.parse_celebrity_info(raw_text, source_type)

        # 生成 System Prompt
        system_prompt = pdf_parser_service.generate_system_prompt(parsed_info, source_type)

        # 创建数据库记录
        celebrity = KnowledgeSource(
            name=parsed_info.get("name", "未知"),
            source_type=source_type,
            author=parsed_info.get("author"),
            birth_year=parsed_info.get("birth_year"),
            death_year=parsed_info.get("death_year"),
            nationality=parsed_info.get("nationality"),
            occupation=parsed_info.get("occupation"),
            biography=parsed_info.get("biography"),
            famous_works=parsed_info.get("famous_works"),
            famous_quotes=parsed_info.get("famous_quotes"),
            personality_traits=parsed_info.get("personality_traits"),
            speech_style=parsed_info.get("speech_style"),
            system_prompt=system_prompt,
            raw_content=raw_text,
            source_pdf_path=file_path,
        )

        async with celebrity_async_session() as session:
            session.add(celebrity)
            await session.flush()  # 获取 celebrity.id

            # 智能分块
            logger.info(f"开始对 {celebrity.name} 的文档进行分块...")
            chunks = chunking_service.chunk_text(
                text=raw_text,
                chunk_size=400,
                overlap=50,
                min_chunk_size=100
            )

            if chunks:
                # 批量生成 embedding
                logger.info(f"生成 {len(chunks)} 个文本块的向量...")
                texts = [chunk["text"] for chunk in chunks]
                # 使用 asyncio.to_thread 在线程池中运行同步函数
                embeddings = await asyncio.to_thread(embedding_service.get_embeddings_batch, texts)

                # 存储到数据库
                for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                    celebrity_chunk = CelebrityChunk(
                        knowledge_source_id=celebrity.id,
                        chunk_text=chunk["text"],
                        chunk_index=chunk["chunk_index"],
                        chunk_metadata=chunk["metadata"],
                        embedding=embedding.tobytes()  # numpy -> bytes
                    )
                    session.add(celebrity_chunk)

                logger.info(f"成功为 {celebrity.name} 创建 {len(chunks)} 个知识块")

            await session.commit()
            await session.refresh(celebrity)
            return CelebrityResponse.model_validate(celebrity)

    except Exception as e:
        logger.error(f"Upload celebrity error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@celebrity_app.delete("/{celebrity_id}")
async def delete_celebrity(celebrity_id: int):
    """删除名人"""
    async with celebrity_async_session() as session:
        result = await session.execute(
            select(KnowledgeSource).where(KnowledgeSource.id == celebrity_id)
        )
        celebrity = result.scalar_one_or_none()
        if not celebrity:
            raise HTTPException(status_code=404, detail="名人不存在")

        # 删除关联的 PDF 文件
        if celebrity.source_pdf_path and os.path.exists(celebrity.source_pdf_path):
            os.remove(celebrity.source_pdf_path)

        await session.delete(celebrity)
        await session.commit()
        return {"message": "删除成功"}


@celebrity_app.websocket("/ws")
async def celebrity_websocket_endpoint(websocket: WebSocket):
    """名人对话 WebSocket 端点"""
    await websocket.accept()
    client_host = websocket.client.host
    logger.info(f"Celebrity WS client connected: {client_host}")

    # 创建独立的orchestrator实例
    orchestrator = CelebrityOrchestratorService()
    session_id = None

    try:
        # 创建会话ID（在连接建立时）
        db = next(get_celebrity_db())
        try:
            session_manager = CelebritySessionManager(db)
            session_id = session_manager.create_session()
            logger.info(f"Created chat session: {session_id}")
        finally:
            db.close()

        while True:
            data = await websocket.receive_text()
            logger.info(f"Celebrity WS received: {data}")

            try:
                msg = json.loads(data)
                user_msg = msg.get("message", "")
                celebrity_ids = msg.get("celebrity_ids", [])
                mode = msg.get("mode", "private")

                # 为每条消息创建新的数据库会话
                db = next(get_celebrity_db())
                try:
                    async for response in orchestrator.handle_message(
                        user_msg, celebrity_ids, mode, session_id, db
                    ):
                        await websocket.send_json(response)
                finally:
                    db.close()

            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "sender": "System",
                    "content": "消息格式错误"
                })

    except WebSocketDisconnect:
        logger.info(f"Celebrity WS client disconnected: {client_host}")
    except Exception as e:
        logger.error(f"Celebrity WebSocket error: {e}")
        await websocket.close()


def init_celebrity_tables():
    """初始化celebrity数据库表"""
    logger.info("Initializing celebrity database tables...")
    # 明确指定要创建的表，确保包含ChatSession和ChatMessage
    Base.metadata.create_all(
        bind=celebrity_sync_engine,
        tables=[
            KnowledgeSource.__table__,
            CelebrityChunk.__table__,
            ChatSession.__table__,
            ChatMessage.__table__
        ]
    )
    logger.info("Celebrity database tables initialized successfully")


async def cleanup_old_sessions():
    """清理7天前的旧会话（定时任务）"""
    logger.info("Starting scheduled cleanup of old chat sessions...")
    db = next(get_celebrity_db())
    try:
        session_manager = CelebritySessionManager(db)
        deleted_count = session_manager.clear_old_sessions(days=7)
        logger.info(f"Scheduled cleanup completed: removed {deleted_count} old sessions")
    except Exception as e:
        logger.error(f"Error during scheduled cleanup: {e}")
    finally:
        db.close()


@celebrity_app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    logger.info("Celebrity app starting up...")

    # 初始化数据库表
    init_celebrity_tables()

    # 启动定时清理任务（每天凌晨3点清理7天前的旧会话）
    scheduler.add_job(
        cleanup_old_sessions,
        'cron',
        hour=3,
        minute=0,
        id='cleanup_old_sessions',
        replace_existing=True
    )
    scheduler.start()
    logger.info("Celebrity app startup completed, scheduler started")


@celebrity_app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理"""
    logger.info("Celebrity app shutting down...")
    scheduler.shutdown()
    logger.info("Scheduler stopped")
