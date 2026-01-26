"""
数字客户子应用 - 销售培训功能
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

from backend.core.database import digital_customer_async_session, get_digital_customer_db, digital_customer_sync_engine
from backend.models.db_models import CustomerProfile, CustomerChunk, ChatSession, ChatMessage, Base
from backend.models.schemas import CustomerProfileResponse
from .services.customer_orchestrator import CustomerOrchestratorService
from .services.session_manager import CustomerSessionManager
from .services.profile_parser import profile_parser_service
from .services.chunking_service import chunking_service
from backend.apps.customer_service.services.embedding_service import embedding_service

# 创建子应用
digital_customer_app = FastAPI(title="VividCrowd Digital Customer API", version="1.0.0")

# 创建定时任务调度器
scheduler = AsyncIOScheduler()

# 文件上传目录
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@digital_customer_app.get("/", response_model=List[CustomerProfileResponse])
async def get_customers():
    """获取所有客户画像列表"""
    async with digital_customer_async_session() as session:
        result = await session.execute(select(CustomerProfile))
        customers = result.scalars().all()
        return [CustomerProfileResponse.model_validate(c) for c in customers]


@digital_customer_app.get("/{customer_id}", response_model=CustomerProfileResponse)
async def get_customer(customer_id: int):
    """获取客户画像详情"""
    async with digital_customer_async_session() as session:
        result = await session.execute(
            select(CustomerProfile).where(CustomerProfile.id == customer_id)
        )
        customer = result.scalar_one_or_none()
        if not customer:
            raise HTTPException(status_code=404, detail="客户画像不存在")
        return CustomerProfileResponse.model_validate(customer)


@digital_customer_app.post("/upload", response_model=CustomerProfileResponse)
async def upload_customer_profile(
    file: UploadFile = File(...),
):
    """上传客户画像文档（PDF或Markdown）并解析创建客户"""
    # 检查文件类型
    if not (file.filename.endswith(".pdf") or file.filename.endswith(".md")):
        raise HTTPException(status_code=400, detail="只支持 PDF 或 Markdown 文件")

    # 保存上传的文件
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        # 根据文件类型提取文本
        raw_text = profile_parser_service.extract_text_from_file(file_path)

        # 使用 LLM 解析结构化信息
        parsed_info = await profile_parser_service.parse_customer_profile(raw_text)

        # 生成 System Prompt
        system_prompt = profile_parser_service.generate_system_prompt(parsed_info)

        # 创建数据库记录
        customer = CustomerProfile(
            name=parsed_info.get("name", "未知客户"),
            age_range=parsed_info.get("age_range"),
            gender=parsed_info.get("gender"),
            occupation=parsed_info.get("occupation"),
            industry=parsed_info.get("industry"),
            personality_traits=parsed_info.get("personality_traits"),
            communication_style=parsed_info.get("communication_style"),
            pain_points=parsed_info.get("pain_points"),
            needs=parsed_info.get("needs"),
            objections=parsed_info.get("objections"),
            system_prompt=system_prompt,
            raw_content=raw_text,
            source_file_path=file_path,
        )

        async with digital_customer_async_session() as session:
            session.add(customer)
            await session.flush()  # 获取 customer.id

            # 智能分块
            logger.info(f"开始对 {customer.name} 的文档进行分块...")
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
                    customer_chunk = CustomerChunk(
                        customer_profile_id=customer.id,
                        chunk_text=chunk["text"],
                        chunk_index=chunk["chunk_index"],
                        chunk_metadata=chunk["metadata"],
                        embedding=embedding.tobytes()  # numpy -> bytes
                    )
                    session.add(customer_chunk)

                logger.info(f"成功为 {customer.name} 创建 {len(chunks)} 个知识块")

            await session.commit()
            await session.refresh(customer)
            return CustomerProfileResponse.model_validate(customer)

    except Exception as e:
        logger.error(f"Upload customer profile error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@digital_customer_app.delete("/{customer_id}")
async def delete_customer(customer_id: int):
    """删除客户画像"""
    async with digital_customer_async_session() as session:
        result = await session.execute(
            select(CustomerProfile).where(CustomerProfile.id == customer_id)
        )
        customer = result.scalar_one_or_none()
        if not customer:
            raise HTTPException(status_code=404, detail="客户画像不存在")

        # 删除关联的文件
        if customer.source_file_path and os.path.exists(customer.source_file_path):
            os.remove(customer.source_file_path)

        await session.delete(customer)
        await session.commit()
        return {"message": "删除成功"}


@digital_customer_app.websocket("/ws")
async def customer_websocket_endpoint(websocket: WebSocket):
    """数字客户对话 WebSocket 端点"""
    await websocket.accept()
    client_host = websocket.client.host
    logger.info(f"Digital Customer WS client connected: {client_host}")

    # 创建独立的orchestrator实例
    orchestrator = CustomerOrchestratorService()
    session_id = None

    try:
        # 创建会话ID（在连接建立时）
        db = next(get_digital_customer_db())
        try:
            session_manager = CustomerSessionManager(db)
            session_id = session_manager.create_session()
            logger.info(f"Created customer chat session: {session_id}")
        finally:
            db.close()

        while True:
            data = await websocket.receive_text()
            logger.info(f"Digital Customer WS received: {data}")

            try:
                msg = json.loads(data)
                user_msg = msg.get("message", "")
                customer_ids = msg.get("customer_ids", [])
                mode = msg.get("mode", "private")

                # 为每条消息创建新的数据库会话
                db = next(get_digital_customer_db())
                try:
                    async for response in orchestrator.handle_message(
                        user_msg, customer_ids, mode, session_id, db
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
        logger.info(f"Digital Customer WS client disconnected: {client_host}")
    except Exception as e:
        logger.error(f"Digital Customer WebSocket error: {e}")
        await websocket.close()


def init_digital_customer_tables():
    """初始化digital_customer数据库表"""
    logger.info("Initializing digital customer database tables...")
    # 明确指定要创建的表
    Base.metadata.create_all(
        bind=digital_customer_sync_engine,
        tables=[
            CustomerProfile.__table__,
            CustomerChunk.__table__,
            ChatSession.__table__,
            ChatMessage.__table__
        ]
    )
    logger.info("Digital customer database tables initialized successfully")


async def cleanup_old_sessions():
    """清理7天前的旧会话（定时任务）"""
    logger.info("Starting scheduled cleanup of old customer chat sessions...")
    db = next(get_digital_customer_db())
    try:
        session_manager = CustomerSessionManager(db)
        deleted_count = session_manager.clear_old_sessions(days=7)
        logger.info(f"Scheduled cleanup completed: removed {deleted_count} old customer sessions")
    except Exception as e:
        logger.error(f"Error during scheduled cleanup: {e}")
    finally:
        db.close()


async def start_scheduler():
    """启动定时任务调度器"""
    # 启动定时清理任务（每天凌晨3点清理7天前的旧会话）
    if not scheduler.running:
        scheduler.add_job(
            cleanup_old_sessions,
            'cron',
            hour=3,
            minute=0,
            id='cleanup_old_customer_sessions',
            replace_existing=True
        )
        scheduler.start()
        logger.info("Digital customer scheduler started")

async def stop_scheduler():
    """停止定时任务调度器"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Digital customer scheduler stopped")

@digital_customer_app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    logger.info("Digital customer app starting up...")

    # 初始化数据库表
    init_digital_customer_tables()

    # 启动定时任务
    await start_scheduler()
    
    logger.info("Digital customer app startup completed")


@digital_customer_app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理"""
    logger.info("Digital customer app shutting down...")
    await stop_scheduler()