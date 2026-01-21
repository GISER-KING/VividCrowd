import asyncio
from typing import List, Dict, Any, AsyncGenerator
from loguru import logger
from sqlalchemy import select
from backend.app.db.database import async_session
from backend.app.db.models import KnowledgeSource
from backend.app.services.celebrity_agent import CelebrityAgent

class CelebrityOrchestratorService:
    """名人对话编排器 - 管理多个名人 Agent 的对话"""

    def __init__(self):
        self.chat_history: List[str] = []

    async def get_celebrity_by_id(self, celebrity_id: int) -> KnowledgeSource | None:
        """根据 ID 获取名人信息"""
        async with async_session() as session:
            result = await session.execute(
                select(KnowledgeSource).where(KnowledgeSource.id == celebrity_id)
            )
            return result.scalar_one_or_none()

    async def handle_message(
        self,
        user_msg: str,
        celebrity_ids: List[int],
        mode: str = "private"
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """处理用户消息

        Args:
            user_msg: 用户消息
            celebrity_ids: 选中的名人 ID 列表
            mode: 对话模式 - 'private' 一对一 / 'group' 群聊

        Yields:
            WebSocket 消息格式: {type, sender, content}
        """
        if not celebrity_ids:
            yield {
                "type": "error",
                "sender": "System",
                "content": "请先选择一位名人进行对话"
            }
            return

        # 记录用户消息到历史
        self.chat_history.append(f"用户: {user_msg}")

        # 获取所有选中的名人
        celebrities = []
        for cid in celebrity_ids:
            celebrity = await self.get_celebrity_by_id(cid)
            if celebrity:
                celebrities.append(celebrity)

        if not celebrities:
            yield {
                "type": "error",
                "sender": "System",
                "content": "未找到选中的名人"
            }
            return

        if mode == "private":
            # 一对一模式：只有一个名人回复
            celebrity = celebrities[0]
            agent = CelebrityAgent(celebrity)

            yield {
                "type": "stream_start",
                "sender": celebrity.name,
                "content": ""
            }

            full_response = ""
            async for chunk in agent.generate_response_stream(
                user_msg,
                self.chat_history,
                mode="private"
            ):
                full_response += chunk
                yield {
                    "type": "stream_chunk",
                    "sender": celebrity.name,
                    "content": chunk
                }

            yield {
                "type": "stream_end",
                "sender": celebrity.name,
                "content": ""
            }

            # 记录回复到历史
            self.chat_history.append(f"{celebrity.name}: {full_response}")

        else:
            # 群聊模式：多个名人依次回复
            for celebrity in celebrities:
                agent = CelebrityAgent(celebrity)

                yield {
                    "type": "stream_start",
                    "sender": celebrity.name,
                    "content": ""
                }

                full_response = ""
                async for chunk in agent.generate_response_stream(
                    user_msg,
                    self.chat_history,
                    mode="group"
                ):
                    full_response += chunk
                    yield {
                        "type": "stream_chunk",
                        "sender": celebrity.name,
                        "content": chunk
                    }

                yield {
                    "type": "stream_end",
                    "sender": celebrity.name,
                    "content": ""
                }

                # 记录回复到历史
                self.chat_history.append(f"{celebrity.name}: {full_response}")

                # 群聊模式下，每个回复之间稍作延迟
                if celebrity != celebrities[-1]:
                    await asyncio.sleep(0.5)

    def clear_history(self):
        """清空对话历史"""
        self.chat_history = []


# 创建全局实例
celebrity_orchestrator_service = CelebrityOrchestratorService()
