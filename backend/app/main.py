import json
import os
import shutil
from typing import List, Dict

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from backend.app.services.orchestrator import orchestrator_service
from backend.app.services.celebrity_orchestrator import celebrity_orchestrator_service
from backend.app.services.pdf_parser import pdf_parser_service
from backend.app.services.customer_service import CustomerServiceOrchestrator, import_qa_from_csv, auto_import_csv_files
from backend.app.models.schemas import WebSocketMessage, CelebrityResponse
from backend.app.db.database import async_session, init_db
from backend.app.db.models import KnowledgeSource
from backend.app.core.config import settings
from loguru import logger

app = FastAPI(title="VividCrowd Backend")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境请修改为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PDF 上传目录
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# CSV 上传目录
CSV_UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads", "csv")
os.makedirs(CSV_UPLOAD_DIR, exist_ok=True)

# 客服编排器
customer_service_orchestrator = CustomerServiceOrchestrator(api_key=os.environ.get("DASHSCOPE_API_KEY"))


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    await init_db()
    logger.info("Database initialized")

    # 自动导入 CSV 文件
    async with async_session() as session:
        try:
            api_key = os.environ.get("DASHSCOPE_API_KEY")
            stats = await auto_import_csv_files(
                db=session,
                csv_dir=CSV_UPLOAD_DIR,
                import_func=import_qa_from_csv,
                api_key=api_key
            )
            if stats["imported"] > 0:
                logger.info(f"自动导入完成: 导入 {stats['imported']}, 跳过 {stats['skipped']}, 失败 {stats['failed']}")
        except Exception as e:
            logger.warning(f"自动导入 CSV 失败: {e}")

    # 初始化客服编排器
    async with async_session() as session:
        try:
            await customer_service_orchestrator.initialize(session)
            logger.info("Customer service orchestrator initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize customer service orchestrator: {e}")


@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/agents")
async def get_agents() -> List[Dict]:
    """获取所有群成员信息"""
    agents_list = []
    for agent in orchestrator_service.agents.values():
        agents_list.append({
            "id": agent.id,
            "name": agent.profile.name,
            "occupation": agent.profile.occupation,
            "personality": "、".join(agent.profile.personality_traits),
            "interests": "、".join(agent.profile.interests)
        })
    return agents_list

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_host = websocket.client.host
    logger.info(f"Client connected: {client_host}")
    
    try:
        while True:
            # 接收用户消息
            data = await websocket.receive_text()
            logger.info(f"Received message: {data}")
            
            # 这里简单假定前端发来的是纯文本，如果是 JSON 可以在此解析
            # 为了更好的结构，我们假设前端发来的是纯文本字符串
            user_msg = data
            
            # 调用编排器处理，并流式返回
            async for response in orchestrator_service.handle_message(user_msg):
                # response 是一个 dict: {type, sender, content}
                await websocket.send_json(response)
                
    except WebSocketDisconnect:
        logger.info(f"Client disconnected: {client_host}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()


# ========== 名人数字分身 API ==========

@app.get("/celebrities", response_model=List[CelebrityResponse])
async def get_celebrities():
    """获取所有名人列表"""
    async with async_session() as session:
        result = await session.execute(select(KnowledgeSource))
        celebrities = result.scalars().all()
        return [CelebrityResponse.model_validate(c) for c in celebrities]


@app.get("/celebrities/{celebrity_id}", response_model=CelebrityResponse)
async def get_celebrity(celebrity_id: int):
    """获取名人详情"""
    async with async_session() as session:
        result = await session.execute(
            select(KnowledgeSource).where(KnowledgeSource.id == celebrity_id)
        )
        celebrity = result.scalar_one_or_none()
        if not celebrity:
            raise HTTPException(status_code=404, detail="名人不存在")
        return CelebrityResponse.model_validate(celebrity)


@app.post("/celebrities/upload", response_model=CelebrityResponse)
async def upload_celebrity(
    file: UploadFile = File(...),
    source_type: str = Form("person")
):
    """上传 PDF 并解析创建名人"""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="只支持 PDF 文件")

    # 保存上传的文件
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        # 提取 PDF 文本
        raw_text = pdf_parser_service.extract_text_from_pdf(file_path)

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

        async with async_session() as session:
            session.add(celebrity)
            await session.commit()
            await session.refresh(celebrity)
            return CelebrityResponse.model_validate(celebrity)

    except Exception as e:
        logger.error(f"Upload celebrity error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/celebrities/{celebrity_id}")
async def delete_celebrity(celebrity_id: int):
    """删除名人"""
    async with async_session() as session:
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


@app.websocket("/ws/celebrity")
async def celebrity_websocket_endpoint(websocket: WebSocket):
    """名人对话 WebSocket 端点"""
    await websocket.accept()
    client_host = websocket.client.host
    logger.info(f"Celebrity WS client connected: {client_host}")

    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Celebrity WS received: {data}")

            try:
                msg = json.loads(data)
                user_msg = msg.get("message", "")
                celebrity_ids = msg.get("celebrity_ids", [])
                mode = msg.get("mode", "private")

                async for response in celebrity_orchestrator_service.handle_message(
                    user_msg, celebrity_ids, mode
                ):
                    await websocket.send_json(response)

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


# ========== 数字客服 API ==========

@app.websocket("/ws/customer-service")
async def customer_service_websocket_endpoint(websocket: WebSocket):
    """客服对话 WebSocket 端点"""
    await websocket.accept()
    client_host = websocket.client.host
    logger.info(f"Customer service WS client connected: {client_host}")

    session_id = None

    try:
        # 创建会话
        async with async_session() as db:
            session_id = await customer_service_orchestrator.create_session(db)
            await websocket.send_json({
                "type": "session_created",
                "session_id": session_id
            })
            logger.info(f"Created customer service session: {session_id}")

        while True:
            data = await websocket.receive_text()
            logger.info(f"Customer service WS received: {data}")

            try:
                msg = json.loads(data)
                user_query = msg.get("message", "")

                if not user_query.strip():
                    await websocket.send_json({
                        "type": "error",
                        "content": "消息不能为空"
                    })
                    continue

                # 非流式处理查询
                async with async_session() as db:
                    result = await customer_service_orchestrator.handle_query(
                        db=db,
                        session_id=session_id,
                        user_query=user_query
                    )
                    await websocket.send_json({
                        'type': 'response',
                        'content': result['response'],
                        'confidence': result['confidence'],
                        'match_type': result['match_type'],
                        'transfer_to_human': result['transfer_to_human'],
                        'matched_topic': result['matched_topic']
                    })

            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "content": "消息格式错误"
                })

    except WebSocketDisconnect:
        logger.info(f"Customer service WS client disconnected: {client_host}")
        if session_id:
            customer_service_orchestrator.end_session(session_id)
    except Exception as e:
        logger.error(f"Customer service WebSocket error: {e}")
        await websocket.close()


@app.post("/customer-service/import-csv")
async def import_customer_service_csv(
    file: UploadFile = File(...),
    clear_existing: bool = Form(True)
):
    """导入客服QA数据（CSV格式）"""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="只支持 CSV 文件")

    # 保存上传的文件
    file_path = os.path.join(CSV_UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        async with async_session() as db:
            result = await import_qa_from_csv(db, file_path, clear_existing)

            # 重新初始化编排器以加载新数据
            await customer_service_orchestrator.initialize(db)

            return result

    except Exception as e:
        logger.error(f"Import CSV error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/customer-service/analytics")
async def get_customer_service_analytics():
    """获取客服系统统计分析数据"""
    try:
        async with async_session() as db:
            analytics = await customer_service_orchestrator.get_analytics(db)
            matcher_stats = customer_service_orchestrator.get_matcher_stats()

            return {
                "analytics": analytics,
                "matcher_stats": matcher_stats
            }

    except Exception as e:
        logger.error(f"Get analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/customer-service/session/{session_id}")
async def get_customer_service_session(session_id: str):
    """获取会话历史记录"""
    try:
        async with async_session() as db:
            history = await customer_service_orchestrator.get_session_history(db, session_id)

            return {
                "session_id": session_id,
                "history": [
                    {
                        "user_query": log.user_query,
                        "bot_response": log.bot_response,
                        "match_type": log.match_type,
                        "confidence_score": log.confidence_score,
                        "timestamp": log.timestamp.isoformat() if log.timestamp else None
                    }
                    for log in history
                ]
            }

    except Exception as e:
        logger.error(f"Get session history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/customer-service/session/{session_id}/rating")
async def set_customer_service_rating(
    session_id: str,
    rating: int = Form(...)
):
    """设置会话评分"""
    try:
        async with async_session() as db:
            await customer_service_orchestrator.set_user_rating(db, session_id, rating)
            return {"message": "评分成功"}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Set rating error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__  == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)