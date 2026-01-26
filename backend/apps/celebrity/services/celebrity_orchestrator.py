import asyncio
from typing import List, Dict, Any, AsyncGenerator
from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.core.database import celebrity_async_session
from backend.models.db_models import KnowledgeSource
from .celebrity_agent import CelebrityAgent
from .session_manager import CelebritySessionManager

class CelebrityOrchestratorService:
    """名人对话编排器 - 管理多个名人 Agent 的对话"""

    def __init__(self):
        # 移除全局chat_history，改为使用Session管理
        pass

    async def get_celebrity_by_id(self, celebrity_id: int) -> KnowledgeSource | None:
        """根据 ID 获取名人信息"""
        async with celebrity_async_session() as session:
            result = await session.execute(
                select(KnowledgeSource).where(KnowledgeSource.id == celebrity_id)
            )
            return result.scalar_one_or_none()

    async def handle_message(
        self,
        user_msg: str,
        celebrity_ids: List[int],
        mode: str = "private",
        session_id: str = None,
        db: Session = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """处理用户消息

        Args:
            user_msg: 用户消息
            celebrity_ids: 选中的名人 ID 列表
            mode: 对话模式 - 'private' 一对一 / 'group' 群聊
            session_id: 会话ID
            db: 数据库会话

        Yields:
            WebSocket 消息格式: {type, sender, content}
        """
        if not session_id or not db:
            yield {
                "type": "error",
                "sender": "System",
                "content": "Session未初始化"
            }
            return

        if not celebrity_ids:
            yield {
                "type": "error",
                "sender": "System",
                "content": "请先选择一位名人进行对话"
            }
            return

        # 创建SessionManager
        session_manager = CelebritySessionManager(db)

        # 获取历史记录
        chat_history = session_manager.get_history(session_id, limit=10)

        # 记录用户消息到数据库
        session_manager.add_message(session_id, "用户", user_msg)
        chat_history.append(f"用户: {user_msg}")

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

            # 创建数据库会话并传递给 Agent
            async with celebrity_async_session() as session:
                agent = CelebrityAgent(celebrity, db_session=session)

                yield {
                    "type": "stream_start",
                    "sender": celebrity.name,
                    "content": ""
                }

                full_response = ""
                async for chunk in agent.generate_response_stream(
                    user_msg,
                    chat_history,
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

                # 记录回复到数据库
                session_manager.add_message(session_id, celebrity.name, full_response)

        else:
            # 群聊模式：多个名人依次回复
            async with celebrity_async_session() as session:
                for celebrity in celebrities:
                    agent = CelebrityAgent(celebrity, db_session=session)

                    yield {
                        "type": "stream_start",
                        "sender": celebrity.name,
                        "content": ""
                    }

                    full_response = ""
                    async for chunk in agent.generate_response_stream(
                        user_msg,
                        chat_history,
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

                    # 记录回复到数据库
                    session_manager.add_message(session_id, celebrity.name, full_response)
                    # 同时更新本地历史，供后续专家参考
                    chat_history.append(f"{celebrity.name}: {full_response}")

                    # 群聊模式下，每个回复之间稍作延迟
                    if celebrity != celebrities[-1]:
                        await asyncio.sleep(0.5)

    # clear_history 方法已移除
    # 历史记录现在通过 SessionManager 管理，使用 clear_old_sessions() 清理旧会话


# 不再创建全局单例，改为在 WebSocket 连接时创建实例
# celebrity_orchestrator_service = CelebrityOrchestratorService()
