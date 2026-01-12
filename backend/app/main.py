import json
from typing import List, Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.services.orchestrator import orchestrator_service
from app.models.schemas import WebSocketMessage
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
