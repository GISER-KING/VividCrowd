"""
数字客户子应用 - 销售培训功能
"""
import os
import json
import shutil
import asyncio
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form, HTTPException, Response
from sqlalchemy import select
from loguru import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from backend.core.database import digital_customer_async_session, get_digital_customer_db, digital_customer_sync_engine
from backend.models.db_models import (
    CustomerProfile, CustomerChunk, ChatSession, ChatMessage, Base,
    TrainingSession, ConversationRound, StageEvaluation, FinalEvaluation
)
from backend.models.schemas import CustomerProfileResponse
from .services.customer_orchestrator import CustomerOrchestratorService
from .services.session_manager import CustomerSessionManager
from .services.profile_parser import profile_parser_service
from .services.chunking_service import chunking_service
from .services.audio_service import transcribe_audio, synthesize_audio
from backend.apps.customer_service.services.embedding_service import embedding_service
from .services.training.training_orchestrator import TrainingOrchestrator
from .services.training.knowledge_service import SalesKnowledgeService
from .services.training.suggestion_generator import SuggestionGenerator
from pydantic import BaseModel

# 创建子应用
digital_customer_app = FastAPI(title="VividCrowd Digital Customer API", version="1.0.0")

# 创建定时任务调度器
scheduler = AsyncIOScheduler()

# 文件上传目录
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


class KnowledgeQueryRequest(BaseModel):
    query: str
    stage: int = None

@digital_customer_app.post("/knowledge/upload")
async def upload_knowledge(
    file: UploadFile = File(...),
):
    """上传销售知识库文件 (仅支持 PDF)"""
    # 检查文件类型
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="只支持 PDF 文件")

    # 保存上传的文件
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        db = next(get_digital_customer_db())
        try:
            service = SalesKnowledgeService(db)
            count = await service.import_file(file_path, file.filename)
            return {"message": "导入成功", "count": count, "filename": file.filename}
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Upload knowledge error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@digital_customer_app.post("/knowledge/query")
async def query_knowledge(
    request: KnowledgeQueryRequest
):
    """查询销售知识库 (RAG Chat)"""
    try:
        db = next(get_digital_customer_db())
        try:
            # 复用 SuggestionGenerator 的逻辑，但作为问答
            generator = SuggestionGenerator(db)
            
            # 1. 检索
            service = SalesKnowledgeService(db)
            relevant_docs = await service.search_knowledge(
                query=request.query, 
                stage=request.stage, 
                limit=3
            )
            
            if not relevant_docs:
                return {"answer": "抱歉，知识库中没有找到相关信息。"}

            # 2. 生成回答
            knowledge_text = "\n".join([f"- {doc}" for doc in relevant_docs])
            prompt = f"""
你是一个专业的销售知识库助手。
请根据以下参考资料回答用户的问题。

【参考资料】：
{knowledge_text}

【用户问题】：{request.query}

请按以下格式回答：
1. **简要解释**：用一句话解释策略或知识点（不要长篇大论）。
2. **参考话术**：提供 1-2 条具体的建议回复话术。
"""
            from dashscope import Generation
            from backend.core.config import settings
            
            response = Generation.call(
                model=settings.MODEL_NAME,
                prompt=prompt,
                api_key=settings.DASHSCOPE_API_KEY,
                result_format='message'
            )

            if response.status_code == 200:
                answer = response.output.choices[0].message.content
                return {"answer": answer, "sources": relevant_docs}
            else:
                return {"answer": "生成回答失败，请稍后再试。"}

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Query knowledge error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@digital_customer_app.post("/audio/transcribe")
async def transcribe_audio_endpoint(file: UploadFile = File(...)):
    """音频转文字 (ASR)"""
    try:
        content = await file.read()
        # 获取扩展名 (如 wav, webm)
        extension = file.filename.split(".")[-1] if "." in file.filename else "wav"
        text = await transcribe_audio(content, extension)
        return {"text": text}
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@digital_customer_app.post("/audio/synthesize")
async def synthesize_audio_endpoint(
    text: str = Form(...),
    voice: str = Form("longxiaochun")
):
    """文字转音频 (TTS)"""
    try:
        audio_data = await synthesize_audio(text, voice)
        return Response(content=audio_data, media_type="audio/mpeg")
    except Exception as e:
        logger.error(f"Synthesis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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


# ==================== 培训相关路由 ====================

@digital_customer_app.post("/training/sessions/start")
async def start_training_session(
    trainee_id: str = Form(...),
    trainee_name: str = Form(...),
    customer_id: int = Form(...)
):
    """开始培训会话"""
    try:
        # 生成会话ID
        import uuid
        session_id = str(uuid.uuid4())

        # 创建培训会话
        training_session = TrainingSession(
            session_id=session_id,
            trainee_id=trainee_id,
            trainee_name=trainee_name,
            customer_profile_id=customer_id,
            current_stage=1,
            current_round=0,
            status="in_progress"
        )

        db = next(get_digital_customer_db())
        try:
            db.add(training_session)
            db.commit()
            db.refresh(training_session)

            return {
                "session_id": session_id,
                "customer_id": customer_id,
                "status": "started"
            }
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Failed to start training session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@digital_customer_app.websocket("/training/ws/{session_id}")
async def training_websocket_endpoint(websocket: WebSocket, session_id: str):
    """培训对话 WebSocket 端点"""
    await websocket.accept()
    client_host = websocket.client.host
    logger.info(f"Training WS client connected: {client_host}, session: {session_id}")

    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Training WS received: {data}")

            try:
                msg = json.loads(data)
                trainee_message = msg.get("message", "")

                if not trainee_message:
                    await websocket.send_json({
                        "type": "error",
                        "sender": "System",
                        "content": "消息不能为空"
                    })
                    continue

                # 为每条消息创建新的数据库会话
                db = next(get_digital_customer_db())
                try:
                    orchestrator = TrainingOrchestrator(db)
                    async for response in orchestrator.handle_training_message(
                        session_id,
                        trainee_message
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
        logger.info(f"Training WS client disconnected: {client_host}")
    except Exception as e:
        logger.error(f"Training WebSocket error: {e}")
        await websocket.close()


@digital_customer_app.get("/training/sessions/{session_id}/evaluation")
async def get_training_evaluation(session_id: str):
    """获取培训评价报告"""
    try:
        db = next(get_digital_customer_db())
        try:
            # 查询培训会话
            result = db.execute(
                select(TrainingSession).where(TrainingSession.session_id == session_id)
            )
            session = result.scalar_one_or_none()

            if not session:
                raise HTTPException(status_code=404, detail="培训会话不存在")

            # 查询最终评价
            result = db.execute(
                select(FinalEvaluation).where(FinalEvaluation.session_id == session.id)
            )
            final_eval = result.scalar_one_or_none()

            if not final_eval:
                raise HTTPException(status_code=404, detail="评价报告尚未生成")

            # 查询阶段评价
            result = db.execute(
                select(StageEvaluation).where(StageEvaluation.session_id == session.id)
            )
            stage_evals = result.scalars().all()

            # 构建返回数据
            return {
                "session_id": session.session_id,
                "trainee_name": session.trainee_name,
                "scenario_name": "销售培训场景",
                "completed_at": session.completed_at.isoformat() if session.completed_at else None,
                "duration_minutes": session.duration_seconds // 60 if session.duration_seconds else 0,
                "scores": {
                    "trust_building_score": final_eval.trust_building_score,
                    "needs_diagnosis_score": final_eval.needs_diagnosis_score,
                    "value_presentation_score": final_eval.value_presentation_score,
                    "objection_handling_score": final_eval.objection_handling_score,
                    "progress_management_score": final_eval.progress_management_score,
                    "total_score": final_eval.total_score,
                    "performance_level": final_eval.performance_level
                },
                "overall_strengths": final_eval.overall_strengths or [],
                "overall_weaknesses": final_eval.overall_weaknesses or [],
                "key_improvements": final_eval.key_improvements or [],
                "uncompleted_tasks": final_eval.uncompleted_tasks or [],
                "stage_details": [
                    {
                        "stage": eval.stage_number,
                        "stage_name": eval.stage_name,
                        "score": eval.score,
                        "rounds_used": eval.rounds_used,
                        "strengths": eval.strengths or [],
                        "weaknesses": eval.weaknesses or [],
                        "suggestions": eval.suggestions or []
                    }
                    for eval in stage_evals
                ],
                "detailed_report": final_eval.detailed_report
            }

        finally:
            db.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get evaluation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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
            ChatMessage.__table__,
            TrainingSession.__table__,
            ConversationRound.__table__,
            StageEvaluation.__table__,
            FinalEvaluation.__table__
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