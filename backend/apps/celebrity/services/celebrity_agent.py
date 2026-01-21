import asyncio
from typing import List, AsyncGenerator
from dashscope import Generation
from loguru import logger
from backend.core.config import settings
from backend.models.db_models import KnowledgeSource

class CelebrityAgent:
    """名人数字分身 Agent"""

    def __init__(self, celebrity: KnowledgeSource):
        self.id = celebrity.id
        self.name = celebrity.name
        self.source_type = celebrity.source_type
        self.system_prompt = celebrity.system_prompt or ""
        self.knowledge_base = celebrity.knowledge_base or ""
        self.raw_content = celebrity.raw_content or ""

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
            # 群聊模式：回复更简短，注意轮流发言
            full_prompt = (
                f"{self.system_prompt}\n\n"
                f"【当前场景】\n"
                f"你正在参与一个智囊团群聊，与其他专家一起讨论用户的问题。\n"
                f"请给出你独特的视角和观点，回复简洁有力（50字以内）。\n\n"
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

        # 如果有原始知识库内容，可以进行简单的关键词匹配检索
        if self.raw_content and len(self.raw_content) > 100:
            # 简单检索：找到包含用户关键词的段落
            relevant_chunks = self._retrieve_relevant_chunks(user_msg)
            if relevant_chunks:
                full_prompt = (
                    f"{self.system_prompt}\n\n"
                    f"【相关知识参考】\n{relevant_chunks}\n\n"
                    f"【当前场景】\n"
                    f"{'智囊团群聊，回复简洁（50字以内）' if mode == 'group' else '一对一私聊'}\n\n"
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
