import asyncio
from typing import List, Dict, Any, AsyncGenerator
from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.core.database import digital_customer_async_session
from backend.models.db_models import CustomerProfile
from .customer_agent import CustomerAgent
from .session_manager import CustomerSessionManager

class CustomerOrchestratorService:
    """数字客户对话编排器 - 管理客户 Agent 的对话"""

    def __init__(self):
        pass

    async def get_customer_by_id(self, customer_id: int) -> CustomerProfile | None:
        """根据 ID 获取客户画像信息"""
        async with digital_customer_async_session() as session:
            result = await session.execute(
                select(CustomerProfile).where(CustomerProfile.id == customer_id)
            )
            return result.scalar_one_or_none()

    async def handle_message(
        self,
        user_msg: str,
        customer_ids: List[int],
        mode: str = "private",
        session_id: str = None,
        db: Session = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """处理销售人员消息

        Args:
            user_msg: 销售人员消息
            customer_ids: 选中的客户 ID 列表
            mode: 对话模式（默认 private）
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

        if not customer_ids:
            yield {
                "type": "error",
                "sender": "System",
                "content": "请先选择一位客户进行对话"
            }
            return

        # 创建SessionManager
        session_manager = CustomerSessionManager(db)

        # 获取历史记录
        chat_history = session_manager.get_history(session_id, limit=10)

        # 记录销售人员消息到数据库
        session_manager.add_message(session_id, "销售人员", user_msg)
        chat_history.append(f"销售人员: {user_msg}")

        # 获取选中的客户（通常只有一个）
        customer = await self.get_customer_by_id(customer_ids[0])

        if not customer:
            yield {
                "type": "error",
                "sender": "System",
                "content": "未找到选中的客户"
            }
            return

        # 创建数据库会话并传递给 Agent
        async with digital_customer_async_session() as session:
            agent = CustomerAgent(customer, db_session=session)

            yield {
                "type": "stream_start",
                "sender": customer.name,
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
                    "sender": customer.name,
                    "content": chunk
                }

            yield {
                "type": "stream_end",
                "sender": customer.name,
                "content": ""
            }

            # 记录回复到数据库
            session_manager.add_message(session_id, customer.name, full_response)
