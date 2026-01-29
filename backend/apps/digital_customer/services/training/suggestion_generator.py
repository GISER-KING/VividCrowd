import json
from typing import List, Dict
from dashscope import Generation
from loguru import logger
from sqlalchemy.orm import Session
from backend.core.config import settings
from .knowledge_service import SalesKnowledgeService

class SuggestionGenerator:
    """AI 销售话术推荐生成器 (RAG-based)"""

    def __init__(self, db: Session):
        self.model = settings.MODEL_NAME
        self.knowledge_service = SalesKnowledgeService(db)

    async def generate_suggestions(
        self,
        stage: int,
        customer_reply: str,
    ) -> List[Dict[str, str]]:
        """
        根据当前阶段和客户回复，生成建议话术
        """
        try:
            # 1. 检索相关知识 (Retrieval)
            # 使用 SalesKnowledgeService 从数据库检索
            relevant_docs = await self.knowledge_service.search_knowledge(
                query=customer_reply, 
                stage=stage, 
                limit=3
            )
            
            knowledge_text = "\n".join([f"- {doc['content']} (来源: {doc['source']})" for doc in relevant_docs])
            
            if not knowledge_text:
                # Fallback specific logic if no knowledge found
                knowledge_text = "暂无具体知识库匹配，请根据通用销售技巧回答。"

            # 2. 构建 Prompt
            prompt = f"""
你是一位金牌销售教练。你的学员正在进行销售实战演练。

【当前阶段】：Stage {stage}
【客户刚刚说】："{customer_reply}"

【参考知识库/话术】：
{knowledge_text}

请根据客户的回复和当前阶段目标，结合参考知识库，为销售学员生成 3 个具体的、不同角度的建议回复（话术）。
要求：
1. 话术要口语化、自然、专业。
2. 每个建议包含两部分：
   - rationale: 简短的策略解释（为什么这么回，不超过20字）
   - script: 具体的参考话术

请直接返回一个 JSON 数组，格式为：
[
    {{"rationale": "策略解释...", "script": "建议话术..."}},
    {{"rationale": "策略解释...", "script": "建议话术..."}}
]
不要包含 Markdown 格式或其他文字。
"""

            # 3. 调用 LLM 生成 (Generation)
            response = Generation.call(
                model=self.model,
                prompt=prompt,
                api_key=settings.DASHSCOPE_API_KEY,
                result_format='message'
            )

            if response.status_code == 200:
                content = response.output.choices[0].message.content
                # 清理可能的 markdown 标记
                content = content.replace("```json", "").replace("```", "").strip()
                try:
                    suggestions = json.loads(content)
                    if isinstance(suggestions, list):
                        return suggestions[:3]
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse suggestions JSON: {content}")
                    # Fallback parsing
                    return []
            
            return []

        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return []