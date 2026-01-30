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
    TrainingSession, ConversationRound, StageEvaluation, FinalEvaluation,
    CustomerProfileRegistry
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


@digital_customer_app.get("/knowledge/files")
async def get_knowledge_files():
    """获取已上传的销售知识库文件列表"""
    try:
        db = next(get_digital_customer_db())
        try:
            from backend.models.db_models import SalesKnowledge
            from sqlalchemy import func

            # 查询所有不同的源文件名及其记录数
            result = db.execute(
                select(
                    SalesKnowledge.source_filename,
                    func.count(SalesKnowledge.id).label('count'),
                    func.max(SalesKnowledge.created_at).label('uploaded_at')
                )
                .where(SalesKnowledge.source_filename.isnot(None))
                .group_by(SalesKnowledge.source_filename)
                .order_by(func.max(SalesKnowledge.created_at).desc())
            )

            files = []
            for row in result:
                files.append({
                    "filename": row.source_filename,
                    "count": row.count,
                    "uploaded_at": row.uploaded_at.isoformat() if row.uploaded_at else None
                })

            return {"files": files}
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Get knowledge files error: {e}")
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

    # 读取文件内容并计算哈希
    file_content = await file.read()
    import hashlib
    file_hash = hashlib.md5(file_content).hexdigest()

    # 检查文件是否已导入
    async with digital_customer_async_session() as session:
        from backend.models.db_models import CustomerProfileRegistry
        result = await session.execute(
            select(CustomerProfileRegistry).where(CustomerProfileRegistry.file_hash == file_hash)
        )
        existing_registry = result.scalar_one_or_none()

        if existing_registry and existing_registry.customer_profile_id:
            logger.info(f"文件已存在: {file.filename}, 返回已有客户画像 ID: {existing_registry.customer_profile_id}")
            # 返回已有的客户画像
            result = await session.execute(
                select(CustomerProfile).where(CustomerProfile.id == existing_registry.customer_profile_id)
            )
            existing_customer = result.scalar_one_or_none()
            if existing_customer:
                return CustomerProfileResponse.model_validate(existing_customer)

    # 保存上传的文件
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(file_content)

    try:
        # 根据文件类型提取文本
        raw_text = profile_parser_service.extract_text_from_file(file_path)

        # 使用 LLM 解析结构化信息
        parsed_info = await profile_parser_service.parse_customer_profile(raw_text)

        # 验证必填字段
        if not parsed_info.get("profile_type"):
            raise HTTPException(
                status_code=400,
                detail="无法从文档中提取客户画像类型，请确保文档包含客户角色描述"
            )

        # 生成 System Prompt
        system_prompt = profile_parser_service.generate_system_prompt(parsed_info)

        # 提取真实姓名和画像类型
        real_name = parsed_info.get("real_name")  # 可能为 None
        profile_type = parsed_info.get("profile_type", "未知客户类型")

        # 创建数据库记录
        customer = CustomerProfile(
            name=real_name,  # 真实客户姓名（可选）
            profile_type=profile_type,  # 客户画像类型（必填）
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
            display_name = customer.name if customer.name else customer.profile_type
            logger.info(f"开始对 {display_name} 的文档进行分块...")
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
                        customer_name=customer.name,  # 冗余字段
                        customer_profile_type=customer.profile_type,  # 冗余字段
                        chunk_text=chunk["text"],
                        chunk_index=chunk["chunk_index"],
                        chunk_metadata=chunk["metadata"],
                        embedding=embedding.tobytes()  # numpy -> bytes
                    )
                    session.add(customer_chunk)

                logger.info(f"成功为 {display_name} 创建 {len(chunks)} 个知识块")

            # 添加注册记录
            from backend.models.db_models import CustomerProfileRegistry
            registry = CustomerProfileRegistry(
                filename=file.filename,
                file_hash=file_hash,
                customer_profile_id=customer.id,
                customer_name=customer.name,
                customer_profile_type=customer.profile_type,
                status="success"
            )
            session.add(registry)
            logger.info(f"已注册文件: {file.filename}")

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

        db = next(get_digital_customer_db())
        try:
            # 获取客户画像信息
            customer = db.query(CustomerProfile).filter(CustomerProfile.id == customer_id).first()
            if not customer:
                raise HTTPException(status_code=404, detail="客户画像不存在")

            # 创建培训会话（包含冗余字段）
            training_session = TrainingSession(
                session_id=session_id,
                trainee_id=trainee_id,
                trainee_name=trainee_name,
                customer_profile_id=customer_id,
                customer_name=customer.name,  # 冗余字段
                customer_profile_type=customer.profile_type,  # 冗余字段
                customer_occupation=customer.occupation,  # 冗余字段
                customer_industry=customer.industry,  # 冗余字段
                current_stage=1,
                current_round=0,
                status="in_progress"
            )

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


@digital_customer_app.get("/training/sessions")
async def get_training_sessions(skip: int = 0, limit: int = 50):
    """获取培训记录列表"""
    try:
        db = next(get_digital_customer_db())
        try:
            # 查询培训会话，关联客户画像和最终评价
            result = db.execute(
                select(TrainingSession, CustomerProfile, FinalEvaluation.id)
                .join(CustomerProfile, TrainingSession.customer_profile_id == CustomerProfile.id)
                .outerjoin(FinalEvaluation, TrainingSession.id == FinalEvaluation.session_id)
                .order_by(TrainingSession.created_at.desc())
                .offset(skip)
                .limit(limit)
            )
            sessions_data = result.all()

            # 构建返回数据
            training_records = []
            for session, profile, final_eval_id in sessions_data:
                training_records.append({
                    "id": session.id,
                    "session_id": session.session_id,
                    "trainee_name": session.trainee_name or "未知",
                    "customer_name": profile.name or profile.profile_type,
                    "customer_profile_type": profile.profile_type,
                    "status": session.status,
                    "current_stage": session.current_stage,
                    "total_rounds": session.total_rounds,
                    "created_at": session.created_at.isoformat() if session.created_at else None,
                    "updated_at": session.updated_at.isoformat() if session.updated_at else None,
                    # 强制设为 True，因为现在支持查看过程详情，无论是否有最终报告
                    "has_report": True,
                })

            return {
                "total": len(training_records),
                "records": training_records
            }
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Failed to fetch training sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@digital_customer_app.get("/training/sessions/{session_id}/evaluation")
async def get_training_evaluation(session_id: str):
    """获取培训评价报告"""
    try:
        db = next(get_digital_customer_db())
        try:
            # 查询培训会话
            # 优先尝试匹配 session_id (UUID)
            result = db.execute(
                select(TrainingSession).where(TrainingSession.session_id == session_id)
            )
            session = result.scalar_one_or_none()

            # 如果没找到，且 session_id 是数字，尝试匹配 id (PK)
            if not session and session_id.isdigit():
                result = db.execute(
                    select(TrainingSession).where(TrainingSession.id == int(session_id))
                )
                session = result.scalar_one_or_none()

            if not session:
                raise HTTPException(status_code=404, detail="培训会话不存在")

            # 查询最终评价
            result = db.execute(
                select(FinalEvaluation).where(FinalEvaluation.session_id == session.id)
            )
            final_eval = result.scalar_one_or_none()

            # 即使没有最终评价，也允许查看详情（查看过程数据）
            # if not final_eval:
            #     raise HTTPException(status_code=404, detail="评价报告尚未生成")

            # 查询阶段评价
            result = db.execute(
                select(StageEvaluation).where(StageEvaluation.session_id == session.id)
            )
            stage_evals = result.scalars().all()

            # 查询所有对话轮次
            result = db.execute(
                select(ConversationRound)
                .where(ConversationRound.session_id == session.id)
                .order_by(ConversationRound.round_number)
            )
            rounds = result.scalars().all()

            # 按阶段分组对话轮次
            rounds_by_stage = {}
            for r in rounds:
                if r.stage not in rounds_by_stage:
                    rounds_by_stage[r.stage] = []
                
                # 解析分析数据
                analysis = r.analysis_data or {}
                if isinstance(analysis, str):
                    try:
                        analysis = json.loads(analysis)
                    except:
                        analysis = {}

                rounds_by_stage[r.stage].append({
                    "round_number": r.round_number,
                    "trainee_message": r.trainee_message,
                    "customer_response": r.customer_response,
                    "quality": r.detected_quality,
                    "issues": analysis.get("issues", []),
                    "suggestions": analysis.get("suggestions", [])
                })

            # 构建返回数据
            return {
                "session_id": session.session_id,
                "trainee_name": session.trainee_name,
                "scenario_name": "销售培训场景",
                "completed_at": session.completed_at.isoformat() if session.completed_at else None,
                "duration_minutes": session.duration_seconds // 60 if session.duration_seconds else 0,
                "scores": {
                    "trust_building_score": final_eval.trust_building_score if final_eval else 0,
                    "needs_diagnosis_score": final_eval.needs_diagnosis_score if final_eval else 0,
                    "value_presentation_score": final_eval.value_presentation_score if final_eval else 0,
                    "objection_handling_score": final_eval.objection_handling_score if final_eval else 0,
                    "progress_management_score": final_eval.progress_management_score if final_eval else 0,
                    "total_score": final_eval.total_score if final_eval else 0,
                    "performance_level": final_eval.performance_level if final_eval else "N/A"
                },
                "overall_strengths": final_eval.overall_strengths if final_eval else [],
                "overall_weaknesses": final_eval.overall_weaknesses if final_eval else [],
                "key_improvements": final_eval.key_improvements if final_eval else [],
                "uncompleted_tasks": final_eval.uncompleted_tasks if final_eval else [],
                "stage_details": [
                    {
                        "stage": eval.stage_number,
                        "stage_name": eval.stage_name,
                        "score": eval.score,
                        "rounds_used": eval.rounds_used,
                        "strengths": eval.strengths or [],
                        "weaknesses": eval.weaknesses or [],
                        "suggestions": eval.suggestions or [],
                        "conversation_rounds": rounds_by_stage.get(eval.stage_number, [])
                    }
                    for eval in stage_evals
                ],
                "detailed_report": final_eval.detailed_report if final_eval else "培训尚未完成或未生成最终报告，以上为已完成阶段的记录。"
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
            CustomerProfileRegistry.__table__,
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

    # 自动导入客户画像文件
    try:
        from backend.apps.digital_customer.services.auto_import_service import auto_import_service
        logger.info("开始自动导入客户画像文件...")
        await auto_import_service.scan_and_import()
    except Exception as e:
        logger.error(f"自动导入失败: {e}")

    logger.info("Digital customer app startup completed")


@digital_customer_app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理"""
    logger.info("Digital customer app shutting down...")
    await stop_scheduler()