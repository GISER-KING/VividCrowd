import asyncio
from typing import List, AsyncGenerator, Optional
from dashscope import Generation
from loguru import logger
from sqlalchemy.orm import Session
from backend.core.config import settings
from backend.models.db_models import CustomerProfile
from .customer_retriever import CustomerRetriever

class CustomerAgent:
    """数字客户 Agent - 用于销售培训"""

    def __init__(self, customer: CustomerProfile, db_session: Optional[Session] = None):
        self.id = customer.id
        self.name = customer.name
        self.system_prompt = customer.system_prompt or ""
        self.raw_content = customer.raw_content or ""

        # 混合检索服务（如果提供了 db_session）
        self.retriever = CustomerRetriever(db_session) if db_session else None

    async def generate_response_stream(
        self,
        user_msg: str,
        chat_history: List[str] = None,
        mode: str = "private"
    ) -> AsyncGenerator[str, None]:
        """流式生成回复

        Args:
            user_msg: 销售人员的消息
            chat_history: 对话历史
            mode: 对话模式（默认 private）
        """
        chat_history = chat_history or []
        context = "\n".join(chat_history[-10:])

        # 构建完整 prompt
        full_prompt = (
            f"{self.system_prompt}\n\n"
            f"【当前场景】\n"
            f"你正在与一位销售人员对话。请保持客户角色，根据你的性格特征、痛点和需求来回应。\n\n"
            f"对话历史：\n{context}\n\n"
            f"销售人员说：{user_msg}\n\n"
            f"请以 {self.name} 的身份回复（保持真实客户的反应，50-150字）："
        )

        # 使用混合检索获取相关知识
        if self.retriever:
            try:
                relevant_context = await self.retriever.retrieve(
                    customer_profile_id=self.id,
                    query=user_msg,
                    top_k=2,
                    use_hybrid=True
                )
                if relevant_context:
                    context_text = "\n".join([item["text"] for item in relevant_context])
                    full_prompt = (
                        f"{self.system_prompt}\n\n"
                        f"【相关背景信息】\n{context_text}\n\n"
                        f"【当前场景】\n"
                        f"你正在与一位销售人员对话。请保持客户角色，根据你的性格特征、痛点和需求来回应。\n\n"
                        f"对话历史：\n{context}\n\n"
                        f"销售人员说：{user_msg}\n\n"
                        f"请以 {self.name} 的身份回复（保持真实客户的反应，50-150字）："
                    )
            except Exception as e:
                logger.warning(f"Retrieval failed: {e}, using basic prompt")

        # 非流式调用 LLM
        try:
            response = Generation.call(
                model=settings.MODEL_NAME,
                prompt=full_prompt,
                api_key=settings.DASHSCOPE_API_KEY,
                result_format='message'
            )

            if response.status_code == 200:
                content = response.output.choices[0].message.content
                yield content
            else:
                logger.error(f"LLM error: {response.message}")
                yield f"[错误: {response.message}]"

        except Exception as e:
            logger.error(f"Customer agent error: {e}")
            yield f"[系统错误: {str(e)}]"
