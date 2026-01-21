"""
数字客服子应用 - 智能客服问答系统
"""
import os
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from loguru import logger

from backend.core.database import async_session
from backend.core.config import settings
from .services.orchestrator import CustomerServiceOrchestrator
from .services.excel_importer import import_qa_from_csv, get_qa_count
from .services.csv_registry import auto_import_csv_files

# 创建子应用
customer_service_app = FastAPI(title="VividCrowd Customer Service API", version="1.0.0")

# 全局编排器实例
orchestrator = CustomerServiceOrchestrator(api_key=settings.DASHSCOPE_API_KEY)

# CSV 文件目录
CSV_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "csv")
os.makedirs(CSV_DIR, exist_ok=True)


@customer_service_app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    logger.info("客服子应用启动中...")

    async with async_session() as db:
        # 自动导入 CSV 文件
        await auto_import_csv_files(
            db=db,
            csv_dir=CSV_DIR,
            import_func=import_qa_from_csv,
            api_key=settings.DASHSCOPE_API_KEY
        )

        # 初始化编排器
        await orchestrator.initialize(db)

    logger.info("客服子应用启动完成")


@customer_service_app.get("/stats")
async def get_stats():
    """获取客服系统统计信息"""
    async with async_session() as db:
        analytics = await orchestrator.get_analytics(db)
        matcher_stats = orchestrator.get_matcher_stats()
        return {
            "analytics": analytics,
            "matcher": matcher_stats
        }


@customer_service_app.get("/qa/count")
async def get_qa_record_count():
    """获取QA记录数量"""
    async with async_session() as db:
        count = await get_qa_count(db)
        return {"count": count}


@customer_service_app.post("/session")
async def create_session():
    """创建新会话"""
    async with async_session() as db:
        session_id = await orchestrator.create_session(db)
        return {"session_id": session_id}


@customer_service_app.get("/session/{session_id}/history")
async def get_session_history(session_id: str):
    """获取会话历史"""
    async with async_session() as db:
        history = await orchestrator.get_session_history(db, session_id)
        return {
            "session_id": session_id,
            "messages": [
                {
                    "user_query": h.user_query,
                    "bot_response": h.bot_response,
                    "match_type": h.match_type,
                    "confidence": h.confidence_score,
                    "timestamp": h.timestamp.isoformat() if h.timestamp else None
                }
                for h in history
            ]
        }


@customer_service_app.post("/session/{session_id}/rating")
async def set_session_rating(session_id: str, rating: int):
    """设置会话评分"""
    if not 1 <= rating <= 5:
        raise HTTPException(status_code=400, detail="评分必须在1-5之间")

    async with async_session() as db:
        await orchestrator.set_user_rating(db, session_id, rating)
        return {"message": "评分成功"}


@customer_service_app.websocket("/ws")
async def customer_service_websocket(websocket: WebSocket):
    """客服对话 WebSocket 端点"""
    await websocket.accept()
    client_host = websocket.client.host
    logger.info(f"Customer Service WS client connected: {client_host}")

    session_id = None
    should_create_new_session = True

    try:
        # 等待客户端第一条消息（可能包含 session_id）
        first_message = await websocket.receive_text()
        logger.info(f"Customer Service WS received first message: {first_message}")

        try:
            msg = json.loads(first_message)

            # 检查是否是会话恢复请求
            if msg.get("type") == "resume_session" and msg.get("session_id"):
                resume_session_id = msg.get("session_id")
                async with async_session() as db:
                    existing_session = await orchestrator.session_manager.get_session(db, resume_session_id)
                    if existing_session:
                        session_id = resume_session_id
                        should_create_new_session = False
                        logger.info(f"恢复现有会话: {session_id}")
                        await websocket.send_json({
                            "type": "session_resumed",
                            "session_id": session_id
                        })
        except json.JSONDecodeError:
            logger.warning("第一条消息不是有效的 JSON，将作为普通消息处理")
            msg = None

        # 如果没有有效的会话恢复请求，创建新会话
        if should_create_new_session:
            async with async_session() as db:
                session_id = await orchestrator.create_session(db)

            await websocket.send_json({
                "type": "session_created",
                "session_id": session_id
            })

        # 处理第一条消息（如果不是会话恢复请求）
        if msg and msg.get("type") != "resume_session":
            user_query = msg.get("message", "")
            stream_mode = msg.get("stream", False)

            if user_query.strip():
                async with async_session() as db:
                    if stream_mode:
                        # 流式模式
                        async for response in orchestrator.handle_query_stream(
                            db=db,
                            session_id=session_id,
                            user_query=user_query
                        ):
                            await websocket.send_json(response)
                    else:
                        # 非流式模式
                        result = await orchestrator.handle_query(
                            db=db,
                            session_id=session_id,
                            user_query=user_query
                        )
                        await websocket.send_json({
                            "type": "response",
                            **result
                        })

        # 继续监听后续消息
        while True:
            data = await websocket.receive_text()
            logger.info(f"Customer Service WS received: {data}")

            try:
                msg = json.loads(data)

                # 处理心跳消息
                if msg.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                    continue

                user_query = msg.get("message", "")
                stream_mode = msg.get("stream", False)

                if not user_query.strip():
                    await websocket.send_json({
                        "type": "error",
                        "content": "消息不能为空"
                    })
                    continue

                async with async_session() as db:
                    if stream_mode:
                        # 流式模式
                        async for response in orchestrator.handle_query_stream(
                            db=db,
                            session_id=session_id,
                            user_query=user_query
                        ):
                            await websocket.send_json(response)
                    else:
                        # 非流式模式
                        result = await orchestrator.handle_query(
                            db=db,
                            session_id=session_id,
                            user_query=user_query
                        )
                        await websocket.send_json({
                            "type": "response",
                            **result
                        })

            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "content": "消息格式错误，请发送JSON格式"
                })

    except WebSocketDisconnect:
        logger.info(f"Customer Service WS client disconnected: {client_host}")
        if session_id:
            orchestrator.end_session(session_id)
    except Exception as e:
        logger.error(f"Customer Service WebSocket error: {e}")
        await websocket.close()
