"""
数字分身子应用 - 名人数字分身功能
"""
import os
import json
import shutil
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form, HTTPException
from sqlalchemy import select
from loguru import logger

from backend.core.database import async_session
from backend.models.db_models import KnowledgeSource
from backend.models.schemas import CelebrityResponse
from .services.celebrity_orchestrator import celebrity_orchestrator_service
from .services.pdf_parser import pdf_parser_service

# 创建子应用
celebrity_app = FastAPI(title="VividCrowd Celebrity API", version="1.0.0")

# PDF 上传目录
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@celebrity_app.get("/", response_model=List[CelebrityResponse])
async def get_celebrities():
    """获取所有名人列表"""
    async with async_session() as session:
        result = await session.execute(select(KnowledgeSource))
        celebrities = result.scalars().all()
        return [CelebrityResponse.model_validate(c) for c in celebrities]


@celebrity_app.get("/{celebrity_id}", response_model=CelebrityResponse)
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


@celebrity_app.post("/upload", response_model=CelebrityResponse)
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


@celebrity_app.delete("/{celebrity_id}")
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


@celebrity_app.websocket("/ws")
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
