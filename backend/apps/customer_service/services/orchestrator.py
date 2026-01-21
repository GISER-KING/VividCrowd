"""
客服编排器 - 协调QA匹配、回复生成和会话管理
"""
import time
from typing import Optional, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from .qa_matcher import QAMatcher
from .response_generator import ResponseGenerator
from .session_manager import SessionManager


class CustomerServiceOrchestrator:
    """客服系统主编排器"""

    def __init__(self, api_key: Optional[str] = None):
        self.qa_matcher = QAMatcher()
        self.response_generator = ResponseGenerator(api_key=api_key)
        self.session_manager = SessionManager()
        self.is_initialized = False

    async def initialize(self, db: AsyncSession):
        """初始化编排器，加载QA数据"""
        if self.is_initialized:
            logger.info("编排器已初始化，跳过")
            return

        logger.info("开始初始化客服编排器...")
        await self.qa_matcher.load_qa_data(db)
        self.is_initialized = True
        logger.info("客服编排器初始化完成")

    async def handle_query(
        self,
        db: AsyncSession,
        session_id: str,
        user_query: str
    ) -> dict:
        """
        处理用户查询（非流式）

        Args:
            db: 数据库会话
            session_id: 会话ID
            user_query: 用户问题

        Returns:
            {
                'response': str,
                'confidence': float,
                'match_type': str,
                'transfer_to_human': bool,
                'matched_topic': str
            }
        """
        start_time = time.time()

        # 1. 匹配QA
        matches = await self.qa_matcher.match(user_query, top_k=1)

        if not matches:
            # 无匹配结果，转人工
            response = self.response_generator._get_transfer_response()
            await self.session_manager.mark_transfer_to_human(db, session_id)
            await self.session_manager.log_message(
                db=db,
                session_id=session_id,
                user_query=user_query,
                bot_response=response,
                matched_qa_id=None,
                match_type='no_match',
                confidence_score=0.0,
                response_time_ms=int((time.time() - start_time) * 1000)
            )

            return {
                'response': response,
                'confidence': 0.0,
                'match_type': 'no_match',
                'transfer_to_human': True,
                'matched_topic': None
            }

        # 2. 获取最佳匹配
        best_match = matches[0]
        matched_qa, confidence, match_type = best_match

        logger.info(
            f"最佳匹配: {matched_qa.topic_name} | "
            f"置信度: {confidence:.3f} | "
            f"类型: {match_type}"
        )

        # 3. 判断是否转人工
        should_transfer = self.qa_matcher.should_transfer_to_human(user_query, best_match)

        if should_transfer:
            await self.session_manager.mark_transfer_to_human(db, session_id)

        # 4. 生成回复
        response = await self.response_generator.generate_response(
            user_query=user_query,
            matched_qa=matched_qa,
            confidence=confidence,
            match_type=match_type
        )

        # 5. 记录日志
        response_time_ms = int((time.time() - start_time) * 1000)
        await self.session_manager.log_message(
            db=db,
            session_id=session_id,
            user_query=user_query,
            bot_response=response,
            matched_qa_id=matched_qa.id,
            match_type=match_type,
            confidence_score=confidence,
            response_time_ms=response_time_ms
        )

        logger.info(f"查询处理完成，耗时: {response_time_ms}ms")

        return {
            'response': response,
            'confidence': confidence,
            'match_type': match_type,
            'transfer_to_human': should_transfer,
            'matched_topic': matched_qa.topic_name
        }

    async def handle_query_stream(
        self,
        db: AsyncSession,
        session_id: str,
        user_query: str
    ) -> AsyncGenerator[dict, None]:
        """
        处理用户查询（流式）

        Yields:
            {
                'type': 'metadata' | 'chunk' | 'end',
                'content': str,
                'confidence': float,
                'match_type': str,
                'transfer_to_human': bool
            }
        """
        start_time = time.time()

        # 1. 匹配QA
        matches = await self.qa_matcher.match(user_query, top_k=1)

        if not matches:
            # 无匹配结果，转人工
            response = self.response_generator._get_transfer_response()
            await self.session_manager.mark_transfer_to_human(db, session_id)

            yield {
                'type': 'metadata',
                'confidence': 0.0,
                'match_type': 'no_match',
                'transfer_to_human': True,
                'matched_topic': None
            }

            yield {
                'type': 'chunk',
                'content': response
            }

            yield {
                'type': 'end'
            }

            await self.session_manager.log_message(
                db=db,
                session_id=session_id,
                user_query=user_query,
                bot_response=response,
                matched_qa_id=None,
                match_type='no_match',
                confidence_score=0.0,
                response_time_ms=int((time.time() - start_time) * 1000)
            )

            return

        # 2. 获取最佳匹配
        best_match = matches[0]
        matched_qa, confidence, match_type = best_match

        logger.info(
            f"最佳匹配: {matched_qa.topic_name} | "
            f"置信度: {confidence:.3f} | "
            f"类型: {match_type}"
        )

        # 3. 判断是否转人工
        should_transfer = self.qa_matcher.should_transfer_to_human(user_query, best_match)

        if should_transfer:
            await self.session_manager.mark_transfer_to_human(db, session_id)

        # 4. 发送元数据
        yield {
            'type': 'metadata',
            'confidence': confidence,
            'match_type': match_type,
            'transfer_to_human': should_transfer,
            'matched_topic': matched_qa.topic_name
        }

        # 5. 流式生成回复
        full_response = ""

        # 如果需要转人工，直接返回转人工消息
        if should_transfer:
            transfer_response = self.response_generator._get_transfer_response()
            full_response = transfer_response
            yield {
                'type': 'chunk',
                'content': transfer_response
            }
        else:
            async for chunk in self.response_generator.generate_response_stream(
                user_query=user_query,
                matched_qa=matched_qa,
                confidence=confidence,
                match_type=match_type
            ):
                full_response += chunk
                yield {
                    'type': 'chunk',
                    'content': chunk
                }

        # 6. 发送结束标记
        yield {
            'type': 'end'
        }

        # 7. 记录日志
        response_time_ms = int((time.time() - start_time) * 1000)
        await self.session_manager.log_message(
            db=db,
            session_id=session_id,
            user_query=user_query,
            bot_response=full_response,
            matched_qa_id=matched_qa.id,
            match_type=match_type,
            confidence_score=confidence,
            response_time_ms=response_time_ms
        )

        logger.info(f"流式查询处理完成，耗时: {response_time_ms}ms")

    async def create_session(self, db: AsyncSession) -> str:
        """创建新会话"""
        return await self.session_manager.create_session(db)

    async def get_session_history(self, db: AsyncSession, session_id: str):
        """获取会话历史"""
        return await self.session_manager.get_session_history(db, session_id)

    async def set_user_rating(self, db: AsyncSession, session_id: str, rating: int):
        """设置用户评分"""
        await self.session_manager.set_user_rating(db, session_id, rating)

    async def get_analytics(self, db: AsyncSession) -> dict:
        """获取统计分析数据"""
        return await self.session_manager.get_analytics(db)

    def get_matcher_stats(self) -> dict:
        """获取匹配引擎统计信息"""
        return self.qa_matcher.get_stats()

    def end_session(self, session_id: str):
        """结束会话"""
        self.session_manager.end_session(session_id)
