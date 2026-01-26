"""
Digital Customer对话会话管理服务
"""
import uuid
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from loguru import logger

from backend.models.db_models import ChatSession, ChatMessage


class CustomerSessionManager:
    """Digital Customer对话会话管理器"""

    def __init__(self, db: Session):
        self.db = db

    def create_session(self, user_id: Optional[str] = None) -> str:
        """创建新会话，返回session_id"""
        session_id = str(uuid.uuid4())
        chat_session = ChatSession(
            session_id=session_id,
            user_id=user_id
        )
        self.db.add(chat_session)
        self.db.commit()
        logger.info(f"Created new customer chat session: {session_id}")
        return session_id

    def add_message(self, session_id: str, sender: str, content: str):
        """添加消息到会话"""
        session = self.db.query(ChatSession).filter(
            ChatSession.session_id == session_id
        ).first()

        if not session:
            raise ValueError(f"Session {session_id} not found")

        message = ChatMessage(
            session_id=session.id,
            sender=sender,
            content=content
        )
        self.db.add(message)

        # 更新会话的updated_at时间
        session.updated_at = datetime.utcnow()

        self.db.commit()
        logger.debug(f"Added message to customer session {session_id}: {sender}")

    def get_history(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[str]:
        """获取会话历史（最近N条）"""
        session = self.db.query(ChatSession).filter(
            ChatSession.session_id == session_id
        ).first()

        if not session:
            logger.warning(f"Session {session_id} not found")
            return []

        messages = self.db.query(ChatMessage).filter(
            ChatMessage.session_id == session.id
        ).order_by(ChatMessage.timestamp.desc()).limit(limit).all()

        # 反转顺序（最早的在前）
        messages.reverse()

        return [f"{msg.sender}: {msg.content}" for msg in messages]

    def clear_old_sessions(self, days: int = 7):
        """清理N天前的旧会话"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        deleted_count = self.db.query(ChatSession).filter(
            ChatSession.updated_at < cutoff_date
        ).delete()

        self.db.commit()
        logger.info(f"Cleaned up {deleted_count} old customer chat sessions (older than {days} days)")
        return deleted_count
