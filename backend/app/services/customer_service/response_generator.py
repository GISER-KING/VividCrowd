"""
LLM约束生成器 - 严格遵循话术的回复生成
根据置信度级别采用不同策略：
- 高置信度(>0.9)：直接返回话术
- 中置信度(0.6-0.9)：LLM严格改写话术
- 低置信度(<0.6)：转人工
"""
import asyncio
from typing import Optional, AsyncGenerator
from dashscope import Generation
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from backend.app.db.models import CustomerServiceQA


def _llm_retry_decorator():
    """LLM调用重试装饰器：3次重试，指数退避（2-10秒）"""
    return retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, ConnectionResetError, TimeoutError, OSError)),
        reraise=True
    )


class ResponseGenerator:
    """LLM约束回复生成器"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def _build_constrained_prompt(
        self,
        user_query: str,
        matched_qa: CustomerServiceQA,
        confidence: float
    ) -> str:
        """构建约束性提示词，强制LLM遵循话术"""

        prompt = f"""你是一位专业的儿童健康管理客服。请严格遵循以下标准话术来回答用户问题。

【用户问题】
{user_query}

【匹配的知识库话题】
主题名称：{matched_qa.topic_name}
典型提问：{matched_qa.typical_question}

【标准话术（必须遵循）】
{matched_qa.standard_script}

【风险提示】
{matched_qa.risk_notes or "无"}

【匹配置信度】
{confidence:.2f}

【重要约束】
1. 必须基于上述标准话术进行回答，不要自行发挥
2. 可以根据用户具体问题对话术进行适当调整，但核心内容不变
3. 回答要自然流畅，像真人客服一样亲切
4. 如有风险提示，请在回答中适当提醒
5. 不要提及"标准话术"、"知识库"等系统信息
6. 称呼用户为"您"或"家长"
7. 回答控制在200字以内

请生成回复："""

        return prompt

    async def generate_response(
        self,
        user_query: str,
        matched_qa: Optional[CustomerServiceQA],
        confidence: float,
        match_type: str
    ) -> str:
        """
        生成回复

        Args:
            user_query: 用户问题
            matched_qa: 匹配的QA记录
            confidence: 置信度分数
            match_type: 匹配类型 ('high_confidence', 'mid_confidence', 'low_confidence')

        Returns:
            回复文本
        """
        # 无匹配 - 引导用户
        if not matched_qa:
            return self._get_guidance_response()

        # 高置信度 - 直接返回话术
        if match_type == 'high_confidence':
            return self._format_direct_response(matched_qa)

        # 中置信度 - LLM改写话术
        if match_type == 'mid_confidence':
            return await self._generate_llm_response(user_query, matched_qa, confidence)

        # 低置信度 - LLM尝试回答并引导
        return await self._generate_llm_response_with_guidance(user_query, matched_qa, confidence)

    async def generate_response_stream(
        self,
        user_query: str,
        matched_qa: Optional[CustomerServiceQA],
        confidence: float,
        match_type: str
    ) -> AsyncGenerator[str, None]:
        """
        流式生成回复

        Yields:
            回复文本片段
        """
        # 无匹配 - 引导用户
        if not matched_qa:
            yield self._get_guidance_response()
            return

        # 高置信度 - 直接返回话术
        if match_type == 'high_confidence':
            response = self._format_direct_response(matched_qa)
            # 模拟流式输出
            for char in response:
                yield char
                await asyncio.sleep(0.01)
            return

        # 中置信度 - LLM流式改写
        if match_type == 'mid_confidence':
            async for chunk in self._generate_llm_response_stream(user_query, matched_qa, confidence):
                yield chunk
            return

        # 低置信度 - LLM尝试回答并引导
        async for chunk in self._generate_llm_response_stream_with_guidance(user_query, matched_qa, confidence):
            yield chunk

    def _format_direct_response(self, qa: CustomerServiceQA) -> str:
        """格式化直接返回的话术"""
        response = qa.standard_script

        # 如果有风险提示，添加温馨提示
        if qa.risk_notes:
            response += f"\n\n温馨提示：{qa.risk_notes}"

        return response

    def _get_transfer_response(self) -> str:
        """获取转人工的标准回复"""
        return (
            "非常抱歉，您的问题需要专业客服为您解答。\n"
            "我正在为您转接人工客服，请稍等片刻...\n\n"
            "您也可以直接拨打客服热线：400-XXX-XXXX"
        )

    def _get_guidance_response(self) -> str:
        """获取引导用户的回复（无匹配时使用）"""
        return (
            "抱歉，我没有完全理解您的问题。\n\n"
            "您可以尝试：\n"
            "1. 更详细地描述您的问题\n"
            "2. 使用关键词，如「挑食」「维生素」「过敏」等\n"
            "3. 参考下方的快捷问题进行提问\n\n"
            "如需人工客服，请直接说「转人工」"
        )

    def _build_guidance_prompt(
        self,
        user_query: str,
        matched_qa: CustomerServiceQA,
        confidence: float
    ) -> str:
        """构建低置信度时的引导提示词"""

        prompt = f"""你是一位专业的儿童健康管理客服。用户的问题与知识库匹配度较低，请尝试理解用户意图并给出帮助。

【用户问题】
{user_query}

【可能相关的知识库话题】
主题名称：{matched_qa.topic_name}
典型提问：{matched_qa.typical_question}
标准话术：{matched_qa.standard_script}
风险提示：{matched_qa.risk_notes or "无"}

【匹配置信度】
{confidence:.2f}（较低）

【回复策略】
1. 如果用户问题与上述话题相关，尝试基于标准话术回答
2. 如果不太相关，礼貌地引导用户更清晰地描述问题
3. 可以询问用户具体想了解哪方面的信息
4. 语气要亲切友好，像真人客服一样
5. 回答控制在150字以内
6. 不要提及"置信度"、"匹配度"等系统信息

请生成回复："""

        return prompt

    async def _generate_llm_response_with_guidance(
        self,
        user_query: str,
        matched_qa: CustomerServiceQA,
        confidence: float
    ) -> str:
        """低置信度时使用LLM生成带引导的回复（带重试机制）"""
        prompt = self._build_guidance_prompt(user_query, matched_qa, confidence)

        @_llm_retry_decorator()
        def _call_llm():
            return Generation.call(
                model='qwen-turbo',
                prompt=prompt,
                api_key=self.api_key,
                result_format='message'
            )

        try:
            response = _call_llm()

            if response.status_code == 200:
                content = response.output.choices[0].message.content
                logger.info(f"LLM生成引导回复成功，长度: {len(content)}")
                return content
            else:
                logger.error(f"LLM调用失败: {response.code} - {response.message}")
                return self._get_guidance_response()

        except Exception as e:
            logger.error(f"LLM调用异常（重试后仍失败）: {e}")
            return self._get_guidance_response()

    async def _generate_llm_response_stream_with_guidance(
        self,
        user_query: str,
        matched_qa: CustomerServiceQA,
        confidence: float
    ) -> AsyncGenerator[str, None]:
        """低置信度时使用LLM流式生成带引导的回复"""
        prompt = self._build_guidance_prompt(user_query, matched_qa, confidence)

        try:
            responses = Generation.call(
                model='qwen-turbo',
                prompt=prompt,
                api_key=self.api_key,
                result_format='message',
                stream=True
            )

            for response in responses:
                if response.status_code == 200:
                    if hasattr(response.output, 'choices') and response.output.choices:
                        delta = response.output.choices[0].message.get('content', '')
                        if delta:
                            yield delta
                else:
                    logger.error(f"LLM流式调用失败: {response.code}")
                    yield self._get_guidance_response()
                    return

        except Exception as e:
            logger.error(f"LLM流式调用异常: {e}")
            yield self._get_guidance_response()

    async def _generate_llm_response(
        self,
        user_query: str,
        matched_qa: CustomerServiceQA,
        confidence: float
    ) -> str:
        """使用LLM生成约束性回复（带重试机制）"""
        prompt = self._build_constrained_prompt(user_query, matched_qa, confidence)

        @_llm_retry_decorator()
        def _call_llm():
            return Generation.call(
                model='qwen-turbo',
                prompt=prompt,
                api_key=self.api_key,
                result_format='message'
            )

        try:
            response = _call_llm()

            if response.status_code == 200:
                content = response.output.choices[0].message.content
                logger.info(f"LLM生成回复成功，长度: {len(content)}")
                return content
            else:
                logger.error(f"LLM调用失败: {response.code} - {response.message}")
                # 降级处理：直接返回话术
                return self._format_direct_response(matched_qa)

        except Exception as e:
            logger.error(f"LLM调用异常（重试后仍失败）: {e}")
            # 降级处理：直接返回话术
            return self._format_direct_response(matched_qa)

    async def _generate_llm_response_stream(
        self,
        user_query: str,
        matched_qa: CustomerServiceQA,
        confidence: float
    ) -> AsyncGenerator[str, None]:
        """使用LLM流式生成约束性回复"""
        prompt = self._build_constrained_prompt(user_query, matched_qa, confidence)

        try:
            responses = Generation.call(
                model='qwen-turbo',
                prompt=prompt,
                api_key=self.api_key,
                result_format='message',
                stream=True
            )

            for response in responses:
                if response.status_code == 200:
                    if hasattr(response.output, 'choices') and response.output.choices:
                        delta = response.output.choices[0].message.get('content', '')
                        if delta:
                            yield delta
                else:
                    logger.error(f"LLM流式调用失败: {response.code}")
                    # 降级处理
                    fallback = self._format_direct_response(matched_qa)
                    yield fallback
                    return

        except Exception as e:
            logger.error(f"LLM流式调用异常: {e}")
            # 降级处理
            fallback = self._format_direct_response(matched_qa)
            yield fallback

    def get_greeting_response(self) -> str:
        """获取问候语回复"""
        return (
            "您好！我是您的专属健康管理客服小助手。\n"
            "我可以解答您关于儿童营养、饮食调理、检测报告解读等方面的问题。\n\n"
            "请问有什么可以帮您的吗？"
        )

    def get_farewell_response(self) -> str:
        """获取告别语回复"""
        return (
            "感谢您的咨询！如果还有其他问题，随时可以联系我们。\n"
            "祝您和宝宝健康快乐！再见~ 👋"
        )
