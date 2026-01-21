"""
会话管理器 - 管理客服会话状态和对话日志
"""
import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from loguru import logger

from backend.models.db_models import CustomerServiceSession, CustomerServiceLog


class SessionManager:
    """会话管理器"""

    def __init__(self):
        self.active_sessions: dict = {}  # session_id -> session_data

    async def create_session(self, db: AsyncSession) -> str:
        """创建新会话"""
        session_id = str(uuid.uuid4())

        session = CustomerServiceSession(
            session_id=session_id,
            start_time=datetime.utcnow(),
            message_count=0,
            avg_confidence=None,
            transfer_to_human=False,
            user_rating=None
        )

        db.add(session)
        await db.commit()

        # 缓存到内存
        self.active_sessions[session_id] = {
            'message_count': 0,
            'confidence_scores': [],
            'transfer_to_human': False,
            'start_time': datetime.utcnow()
        }

        logger.info(f"创建新会话: {session_id}")
        return session_id

    async def get_session(self, db: AsyncSession, session_id: str) -> Optional[CustomerServiceSession]:
        """获取会话记录"""
        result = await db.execute(
            select(CustomerServiceSession).where(
                CustomerServiceSession.session_id == session_id
            )
        )
        return result.scalar_one_or_none()

    async def log_message(
        self,
        db: AsyncSession,
        session_id: str,
        user_query: str,
        bot_response: str,
        matched_qa_id: Optional[int] = None,
        match_type: Optional[str] = None,
        confidence_score: Optional[float] = None,
        response_time_ms: Optional[int] = None
    ):
        """记录对话日志"""
        log_entry = CustomerServiceLog(
            session_id=session_id,
            user_query=user_query,
            bot_response=bot_response,
            matched_qa_id=matched_qa_id,
            match_type=match_type,
            confidence_score=confidence_score,
            response_time_ms=response_time_ms,
            timestamp=datetime.utcnow()
        )

        db.add(log_entry)

        # 更新会话统计
        if session_id in self.active_sessions:
            self.active_sessions[session_id]['message_count'] += 1
            if confidence_score is not None:
                self.active_sessions[session_id]['confidence_scores'].append(confidence_score)

        # 更新数据库中的会话记录
        await self._update_session_stats(db, session_id, confidence_score)

        await db.commit()

        logger.info(f"记录对话日志: session={session_id}, match_type={match_type}, confidence={confidence_score}")

    async def _update_session_stats(
        self,
        db: AsyncSession,
        session_id: str,
        new_confidence: Optional[float]
    ):
        """更新会话统计信息"""
        session_data = self.active_sessions.get(session_id, {})
        message_count = session_data.get('message_count', 0) + 1
        confidence_scores = session_data.get('confidence_scores', [])

        if new_confidence is not None:
            confidence_scores = confidence_scores + [new_confidence]

        avg_confidence = None
        if confidence_scores:
            avg_confidence = sum(confidence_scores) / len(confidence_scores)

        await db.execute(
            update(CustomerServiceSession)
            .where(CustomerServiceSession.session_id == session_id)
            .values(
                message_count=message_count,
                avg_confidence=avg_confidence
            )
        )

    async def mark_transfer_to_human(self, db: AsyncSession, session_id: str):
        """标记会话转人工"""
        await db.execute(
            update(CustomerServiceSession)
            .where(CustomerServiceSession.session_id == session_id)
            .values(transfer_to_human=True)
        )
        await db.commit()

        if session_id in self.active_sessions:
            self.active_sessions[session_id]['transfer_to_human'] = True

        logger.info(f"会话 {session_id} 已转人工")

    async def set_user_rating(self, db: AsyncSession, session_id: str, rating: int):
        """设置用户评分"""
        if not 1 <= rating <= 5:
            raise ValueError("评分必须在1-5之间")

        await db.execute(
            update(CustomerServiceSession)
            .where(CustomerServiceSession.session_id == session_id)
            .values(user_rating=rating)
        )
        await db.commit()

        logger.info(f"会话 {session_id} 用户评分: {rating}")

    async def get_session_history(
        self,
        db: AsyncSession,
        session_id: str
    ) -> List[CustomerServiceLog]:
        """获取会话历史记录"""
        result = await db.execute(
            select(CustomerServiceLog)
            .where(CustomerServiceLog.session_id == session_id)
            .order_by(CustomerServiceLog.timestamp)
        )
        return result.scalars().all()

    async def get_analytics(self, db: AsyncSession) -> dict:
        """获取统计分析数据"""
        # 获取所有会话
        sessions_result = await db.execute(select(CustomerServiceSession))
        sessions = sessions_result.scalars().all()

        # 获取所有日志
        logs_result = await db.execute(select(CustomerServiceLog))
        logs = logs_result.scalars().all()

        if not sessions:
            return {
                'total_sessions': 0,
                'total_messages': 0,
                'avg_confidence': None,
                'transfer_rate': 0,
                'avg_rating': None,
                'match_type_distribution': {}
            }

        total_sessions = len(sessions)
        total_messages = sum(s.message_count or 0 for s in sessions)
        transfer_count = sum(1 for s in sessions if s.transfer_to_human)
        ratings = [s.user_rating for s in sessions if s.user_rating is not None]

        # 计算平均置信度
        confidences = [s.avg_confidence for s in sessions if s.avg_confidence is not None]
        avg_confidence = sum(confidences) / len(confidences) if confidences else None

        # 计算平均评分
        avg_rating = sum(ratings) / len(ratings) if ratings else None

        # 匹配类型分布
        match_types = {}
        for log in logs:
            if log.match_type:
                match_types[log.match_type] = match_types.get(log.match_type, 0) + 1

        return {
            'total_sessions': total_sessions,
            'total_messages': total_messages,
            'avg_confidence': round(avg_confidence, 3) if avg_confidence else None,
            'transfer_rate': round(transfer_count / total_sessions * 100, 2) if total_sessions > 0 else 0,
            'avg_rating': round(avg_rating, 2) if avg_rating else None,
            'match_type_distribution': match_types
        }

    def end_session(self, session_id: str):
        """结束会话（从内存中移除）"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            logger.info(f"会话 {session_id} 已结束")
