import asyncio
from typing import List, AsyncGenerator, Optional
from dashscope import Generation
from loguru import logger
from sqlalchemy.orm import Session
from backend.core.config import settings
from backend.models.db_models import KnowledgeSource
from .celebrity_retriever import CelebrityRetriever

class CelebrityAgent:
    """名人数字分身 Agent"""

    def __init__(self, celebrity: KnowledgeSource, db_session: Optional[Session] = None):
        self.id = celebrity.id
        self.name = celebrity.name
        self.source_type = celebrity.source_type
        self.system_prompt = celebrity.system_prompt or ""
        self.knowledge_base = celebrity.knowledge_base or ""
        self.raw_content = celebrity.raw_content or ""

        # 混合检索服务（如果提供了 db_session）
        self.retriever = CelebrityRetriever(db_session) if db_session else None

    async def generate_response_stream(
        self,
        user_msg: str,
        chat_history: List[str] = None,
        mode: str = "private"
    ) -> AsyncGenerator[str, None]:
        """流式生成回复

        Args:
            user_msg: 用户消息
            chat_history: 对话历史
            mode: 对话模式 - 'private' 一对一 / 'group' 群聊
        """
        chat_history = chat_history or []
        context = "\n".join(chat_history[-10:])

        # 构建完整 prompt
        if mode == "group":
            # 群聊模式：应用去重和互动优化
            expert_replies = [msg for msg in chat_history if not msg.startswith("用户:")]

            if expert_replies:
                interaction_hint = (
                    f"【其他专家观点】\n"
                    f"{chr(10).join(expert_replies[-2:])}\n\n"
                    f"【回复要求】\n"
                    f"1. 避免重复上述专家已提到的观点\n"
                    f"2. 可以赞同、补充或提出不同看法\n"
                    f"3. 从你独特的视角给出见解\n"
                    f"4. 回复简洁有力（50字以内）\n\n"
                )
            else:
                interaction_hint = "【回复要求】\n请给出你独特的视角和观点，回复简洁有力（50字以内）。\n\n"

            full_prompt = (
                f"{self.system_prompt}\n\n"
                f"【当前场景】\n"
                f"你正在参与一个智囊团群聊，与其他专家一起讨论用户的问题。\n\n"
                f"{interaction_hint}"
                f"对话历史：\n{context}\n\n"
                f"用户最新问题：{user_msg}\n\n"
                f"请以 {self.name} 的身份回复："
            )
        else:
            # 私聊模式：可以更详细
            full_prompt = (
                f"{self.system_prompt}\n\n"
                f"【当前场景】\n"
                f"用户正在与你进行一对一私聊，请认真回答他们的问题。\n\n"
                f"对话历史：\n{context}\n\n"
                f"用户最新问题：{user_msg}\n\n"
                f"请以 {self.name} 的身份回复（100-200字为宜）："
            )

        # 使用混合检索获取相关知识
        if self.retriever:
            try:
                # 优化1：构建增强的检索query，结合对话历史
                # 取最近2-3条对话作为上下文，避免query过长
                recent_history = chat_history[-3:] if len(chat_history) > 0 else []
                if recent_history:
                    # 格式：[上下文] 当前问题
                    enhanced_query = f"{' '.join(recent_history[-2:])} {user_msg}"
                else:
                    enhanced_query = user_msg

                relevant_context = await self.retriever.get_context_for_query(
                    knowledge_source_id=self.id,
                    query=enhanced_query,
                    top_k=3,
                    use_hybrid=True
                )
                if relevant_context:
                    # 优化2&3：在群聊模式下，分析前面专家的回复，实现去重和互动
                    if mode == "group":
                        # 提取前面专家的回复（排除用户消息）
                        expert_replies = [msg for msg in chat_history if not msg.startswith("用户:")]

                        if expert_replies:
                            # 构建去重和互动提示
                            interaction_hint = (
                                f"【其他专家观点】\n"
                                f"{chr(10).join(expert_replies[-2:])}\n\n"  # 最近2条专家回复
                                f"【回复要求】\n"
                                f"1. 避免重复上述专家已提到的观点\n"
                                f"2. 可以赞同、补充或提出不同看法\n"
                                f"3. 从你独特的视角给出见解\n"
                                f"4. 回复简洁有力（50字以内）\n\n"
                            )
                        else:
                            interaction_hint = "【回复要求】\n回复简洁有力（50字以内）\n\n"

                        full_prompt = (
                            f"{self.system_prompt}\n\n"
                            f"【相关知识参考】\n{relevant_context}\n\n"
                            f"【当前场景】\n你正在参与智囊团群聊，与其他专家一起讨论问题。\n\n"
                            f"{interaction_hint}"
                            f"对话历史：\n{context}\n\n"
                            f"用户最新问题：{user_msg}\n\n"
                            f"请以 {self.name} 的身份回复："
                        )
                    else:
                        # 私聊模式保持原样
                        full_prompt = (
                            f"{self.system_prompt}\n\n"
                            f"【相关知识参考】\n{relevant_context}\n\n"
                            f"【当前场景】\n一对一私聊\n\n"
                            f"对话历史：\n{context}\n\n"
                            f"用户最新问题：{user_msg}\n\n"
                            f"请以 {self.name} 的身份回复，如果使用了参考知识，请在末尾标注来源："
                        )
            except Exception as e:
                logger.warning(f"Hybrid retrieval failed for {self.name}: {e}, falling back to basic prompt")
        elif self.raw_content and len(self.raw_content) > 100:
            # 降级方案：如果没有 retriever，使用简单关键词检索
            relevant_chunks = self._retrieve_relevant_chunks(user_msg)
            if relevant_chunks:
                # 应用相同的去重和互动优化
                if mode == "group":
                    expert_replies = [msg for msg in chat_history if not msg.startswith("用户:")]
                    if expert_replies:
                        interaction_hint = (
                            f"【其他专家观点】\n"
                            f"{chr(10).join(expert_replies[-2:])}\n\n"
                            f"【回复要求】\n"
                            f"1. 避免重复上述专家已提到的观点\n"
                            f"2. 可以赞同、补充或提出不同看法\n"
                            f"3. 从你独特的视角给出见解\n"
                            f"4. 回复简洁有力（50字以内）\n\n"
                        )
                    else:
                        interaction_hint = "【回复要求】\n回复简洁有力（50字以内）\n\n"

                    full_prompt = (
                        f"{self.system_prompt}\n\n"
                        f"【相关知识参考】\n{relevant_chunks}\n\n"
                        f"【当前场景】\n你正在参与智囊团群聊，与其他专家一起讨论问题。\n\n"
                        f"{interaction_hint}"
                        f"对话历史：\n{context}\n\n"
                        f"用户最新问题：{user_msg}\n\n"
                        f"请以 {self.name} 的身份回复："
                    )
                else:
                    full_prompt = (
                        f"{self.system_prompt}\n\n"
                        f"【相关知识参考】\n{relevant_chunks}\n\n"
                        f"【当前场景】\n一对一私聊\n\n"
                        f"对话历史：\n{context}\n\n"
                        f"用户最新问题：{user_msg}\n\n"
                        f"请以 {self.name} 的身份回复，如果使用了参考知识，请在末尾标注来源："
                    )

        # 调用 DashScope API
        max_retries = 1
        for attempt in range(max_retries + 1):
            try:
                logger.info(f"CelebrityAgent {self.name} calling API (Attempt {attempt + 1})...")

                if not settings.DASHSCOPE_API_KEY:
                    logger.error("DASHSCOPE_API_KEY is not set!")
                    yield "[配置错误：API Key 缺失]"
                    return

                responses = Generation.call(
                    model=settings.MODEL_NAME,
                    prompt=full_prompt,
                    api_key=settings.DASHSCOPE_API_KEY,
                    temperature=0.7,
                    max_tokens=500 if mode == "private" else 150,
                    stream=True,
                    result_format='message'
                )

                last_len = 0
                for response in responses:
                    if response.status_code == 200:
                        full_content = response.output.choices[0].message.content
                        if full_content:
                            chunk = full_content[last_len:]
                            if chunk:
                                yield chunk
                                last_len = len(full_content)
                        await asyncio.sleep(0.01)
                    else:
                        logger.error(f"DashScope Error: {response.code} - {response.message}")
                        yield f"[Error: {response.message}]"
                        return

                logger.info(f"CelebrityAgent {self.name} generation finished.")
                break

            except Exception as e:
                logger.error(f"CelebrityAgent {self.name} error (Attempt {attempt + 1}): {e}")
                if attempt < max_retries:
                    logger.info("Retrying...")
                    await asyncio.sleep(0.5)
                    continue
                else:
                    yield "抱歉，我暂时无法回答，请稍后再试。"

    def _retrieve_relevant_chunks(self, query: str, max_chunks: int = 3) -> str:
        """简单的关键词检索

        将原始内容分段，找到包含查询关键词的段落
        """
        if not self.raw_content:
            return ""

        # 将内容按段落分割
        paragraphs = self.raw_content.split("\n\n")
        paragraphs = [p.strip() for p in paragraphs if len(p.strip()) > 50]

        # 简单匹配：找到包含查询词的段落
        query_words = query.replace("？", "").replace("。", "").replace("，", "").split()
        scored_paragraphs = []

        for para in paragraphs:
            score = sum(1 for word in query_words if word in para)
            if score > 0:
                scored_paragraphs.append((score, para))

        # 按得分排序，取前几个
        scored_paragraphs.sort(key=lambda x: x[0], reverse=True)
        top_chunks = [p[1][:500] for p in scored_paragraphs[:max_chunks]]

        return "\n---\n".join(top_chunks)
