"""
数字分身子应用 - 名人数字分身功能
"""
import os
import json
import shutil
import asyncio
from typing import List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form, HTTPException, Request, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select
from loguru import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import httpx

from backend.core.database import celebrity_async_session, get_celebrity_db, celebrity_sync_engine
from backend.models.db_models import KnowledgeSource, CelebrityChunk, ChatSession, ChatMessage, Base
from backend.models.schemas import CelebrityResponse
from backend.core.config import settings
from .services.celebrity_orchestrator import CelebrityOrchestratorService
from .services.session_manager import CelebritySessionManager
from .services.pdf_parser import pdf_parser_service
from .services.chunking_service import chunking_service
from backend.apps.customer_service.services.embedding_service import embedding_service
from .services.audio_service import synthesize_audio, transcribe_audio
from .services.audio_upload_service import audio_upload_service
from .services.video_service import celebrity_video_service

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


# === 数字人视频相关API ===

class VideoGenerateRequest(BaseModel):
    """视频生成请求"""
    text: str
    audio_url: Optional[str] = None
    sync: bool = True


@celebrity_app.post("/digital-human/generate-video")
async def generate_digital_human_video(request: VideoGenerateRequest):
    """
    生成名人数字人视频

    流程:
    1. 如果提供了 audio_url，直接使用
    2. 如果没提供 audio_url，先调用 TTS 生成音频
    3. 将音频上传到 OSS 获取公网 URL
    4. 调用火山引擎接口生成视频

    Args:
        text: 要说的文本内容
        audio_url: 可选的音频URL
        sync: 是否同步等待生成完成（默认True）

    Returns:
        { "video_url": "..." }
    """
    try:
        logger.info(f"[Celebrity Digital Human] 收到视频生成请求: text={request.text[:50]}..., sync={request.sync}")

        # 检查火山引擎配置
        if not settings.CELEBRITY_VOLCENGINE_ACCESS_KEY or not settings.CELEBRITY_VOLCENGINE_SECRET_KEY:
            raise HTTPException(status_code=400, detail="火山引擎未配置，请设置 CELEBRITY_VOLCENGINE_ACCESS_KEY 和 CELEBRITY_VOLCENGINE_SECRET_KEY")

        # 准备音频 URL
        audio_url = request.audio_url
        if not audio_url:
            # Step A: TTS 生成
            logger.info("[Celebrity Digital Human] 正在进行 TTS 生成...")
            audio_bytes = await synthesize_audio(request.text)

            # Step B: OSS 上传
            if not settings.CELEBRITY_OSS_ACCESS_KEY_ID or not settings.CELEBRITY_OSS_BUCKET_NAME:
                raise HTTPException(status_code=400, detail="OSS 未配置，无法上传音频。请设置 CELEBRITY_OSS_ACCESS_KEY_ID 和 CELEBRITY_OSS_BUCKET_NAME")

            logger.info("[Celebrity Digital Human] 正在上传音频到 OSS...")
            audio_url = audio_upload_service.upload_audio(audio_bytes, file_extension="mp3")
            logger.info(f"[Celebrity Digital Human] 音频准备就绪: {audio_url}")

        # 调用火山引擎生成视频
        if not celebrity_video_service.cached_resource_id and not settings.CELEBRITY_IMAGE_URL:
            raise HTTPException(status_code=400, detail="未配置名人形象图片URL (CELEBRITY_IMAGE_URL)")

        if request.sync:
            # 同步调用：先创建(如需)再生成
            if not celebrity_video_service.cached_resource_id:
                # 获取图片的真实URL（处理OSS签名）
                raw_image_path = settings.CELEBRITY_IMAGE_URL
                # 如果不是HTTP URL，则通过OSS生成签名URL
                if not raw_image_path.startswith("http"):
                    image_url = audio_upload_service.get_file_url(raw_image_path)
                else:
                    image_url = raw_image_path

                await celebrity_video_service.create_avatar(image_url)

            video_url = await celebrity_video_service.generate_video(audio_url)

            # 将火山引擎URL转换为代理URL，解决CORS问题
            from urllib.parse import quote
            proxy_url = f"/celebrity/digital-human/proxy-video?url={quote(video_url)}"
            logger.info(f"[Celebrity Digital Human] 原始URL: {video_url}")
            logger.info(f"[Celebrity Digital Human] 代理URL: {proxy_url}")

            return {"video_url": proxy_url}
        else:
            video_url = await celebrity_video_service.generate_video(audio_url)

            from urllib.parse import quote
            proxy_url = f"/celebrity/digital-human/proxy-video?url={quote(video_url)}"

            return {"video_url": proxy_url}

    except Exception as e:
        logger.error(f"[Celebrity Digital Human] 视频生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"视频生成失败: {str(e)}")


@celebrity_app.get("/digital-human/proxy-video")
async def proxy_video(url: str):
    """
    视频代理端点 - 解决CORS问题

    通过后端下载火山引擎视频并转发给前端，绕过CORS限制

    Args:
        url: 火山引擎视频URL

    Returns:
        StreamingResponse: 视频流
    """
    try:
        logger.info(f"[Celebrity Video Proxy] 代理请求: {url[:100]}...")

        # 定义异步生成器
        async def iterfile():
            async with httpx.AsyncClient() as client:
                # 开启流式下载，timeout设置长一点防止大视频断开
                async with client.stream("GET", url, timeout=60.0) as response:
                    if response.status_code != 200:
                        logger.error(f"代理视频失败，状态码: {response.status_code}")
                        # 这里不能 raise HTTPException，因为响应已经开始了，只能中断流
                        return

                    # 转发数据块
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        yield chunk

        # 注意：为了获取 header 信息，我们需要先发起一个 HEAD 请求或者简化处理
        # 简单起见，这里直接返回流，浏览器会自动处理 Content-Type
        return StreamingResponse(
            iterfile(),
            media_type="video/mp4" 
        )

    except Exception as e:
        logger.error(f"[Celebrity Video Proxy] 代理失败: {e}")
        # 如果连接还没建立，可以返回 500
        raise HTTPException(status_code=500, detail=f"视频代理失败: {str(e)}")


@celebrity_app.api_route("/digital-human/proxy-video", methods=["GET", "HEAD"])
async def proxy_video(url: str, request: Request):
    """
    视频代理端点 (修复版)
    1. 支持 302 重定向
    2. 支持 HEAD 请求 (解决 405 错误)
    3. 透传 Content-Type 和 Content-Length
    """
    try:
        if not url:
             raise HTTPException(status_code=400, detail="Missing URL")
             
        logger.info(f"[Celebrity Video Proxy] ({request.method}) 代理请求: {url[:60]}...")

        # 1. 配置 Client 自动跟随重定向 (解决 302 错误)
        async with httpx.AsyncClient(follow_redirects=True, verify=False) as client:
            
            # 如果是 HEAD 请求，只获取 Header 不下载内容
            if request.method == "HEAD":
                resp = await client.head(url, timeout=10.0)
                headers = {
                    "Content-Type": resp.headers.get("Content-Type", "video/mp4"),
                    "Content-Length": resp.headers.get("Content-Length"),
                    "Accept-Ranges": "bytes"
                }
                # 过滤掉 None 的 header
                headers = {k: v for k, v in headers.items() if v is not None}
                return Response(status_code=200, headers=headers)

            # 2. 如果是 GET 请求，进行流式传输
            async def iterfile():
                try:
                    # stream=True 配合 follow_redirects=True
                    async with client.stream("GET", url, timeout=60.0) as response:
                        if response.status_code >= 400:
                            logger.error(f"代理视频源返回错误: {response.status_code}")
                            return 

                        # 转发数据块
                        async for chunk in response.aiter_bytes(chunk_size=8192):
                            yield chunk
                except Exception as e:
                    logger.error(f"流传输中断: {e}")

            # 先发一个 HEAD 请求获取必要的 Response Headers (为了浏览器进度条)
            # 注意：这里会多一次轻量请求，但能保证兼容性
            meta_resp = await client.head(url, timeout=10.0)
            media_type = meta_resp.headers.get("Content-Type", "video/mp4")
            content_length = meta_resp.headers.get("Content-Length")
            
            headers = {"Accept-Ranges": "bytes"}
            if content_length:
                headers["Content-Length"] = content_length

            return StreamingResponse(
                iterfile(),
                media_type=media_type,
                headers=headers
            )

    except Exception as e:
        logger.error(f"[Celebrity Video Proxy] 代理失败: {e}")
        raise HTTPException(status_code=500, detail=f"视频代理失败: {str(e)}")


@celebrity_app.post("/digital-human/transcribe-audio")
async def transcribe_audio_endpoint(file: UploadFile = File(...)):
    """
    语音识别端点 - 将音频转换为文本

    Args:
        file: 音频文件

    Returns:
        { "text": "识别出的文本" }
    """
    try:
        logger.info(f"[Celebrity Audio Transcribe] 收到音频文件: {file.filename}")

        # 读取文件内容
        file_content = await file.read()

        # 获取文件扩展名
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'wav'

        # 调用语音识别
        text = await transcribe_audio(file_content, file_extension)

        logger.info(f"[Celebrity Audio Transcribe] 识别成功: {text}")

        return {"text": text}

    except Exception as e:
        logger.error(f"[Celebrity Audio Transcribe] 识别失败: {e}")
        raise HTTPException(status_code=500, detail=f"语音识别失败: {str(e)}")


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
