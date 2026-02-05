"""
面试问题生成器 - 基于RAG检索生成问题
"""
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI

from backend.apps.digital_interviewer.services.knowledge_service import InterviewKnowledgeService


class QuestionGenerator:
    """面试问题生成器"""

    def __init__(
        self,
        knowledge_service: InterviewKnowledgeService,
        api_key: str = None,
        base_url: str = None
    ):
        """初始化问题生成器"""
        self.knowledge_service = knowledge_service
        self.client = AsyncOpenAI(
            api_key=api_key or "sk-xxx",
            base_url=base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        self.model = "qwen-max"

        # 已使用的问题（避免重复）
        self.used_questions: List[str] = []

    async def generate_question(
        self,
        interview_type: str,
        difficulty_level: str = "medium",
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        生成面试问题

        Args:
            interview_type: 面试类型
            difficulty_level: 难度级别
            context: 上下文（如之前的对话）

        Returns:
            问题数据
        """
        # 检索相关知识
        query = f"{interview_type} {difficulty_level} 面试问题"
        if context:
            query += f" {context}"

        knowledge_results = await self.knowledge_service.search_knowledge(
            query=query,
            interview_type=interview_type,
            top_k=3
        )

        # 构建提示词
        prompt = self._build_question_prompt(
            interview_type=interview_type,
            difficulty_level=difficulty_level,
            knowledge_results=knowledge_results,
            context=context
        )

        # 调用LLM生成问题
        messages = [
            {"role": "system", "content": "你是一位专业的面试官，擅长提出有深度的面试问题。"},
            {"role": "user", "content": prompt}
        ]

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.8
        )

        question = response.choices[0].message.content.strip()

        # 记录已使用的问题
        self.used_questions.append(question)

        return {
            "question": question,
            "difficulty_level": difficulty_level,
            "knowledge_sources": [k['content'] for k in knowledge_results]
        }

    def _build_question_prompt(
        self,
        interview_type: str,
        difficulty_level: str,
        knowledge_results: List[Dict[str, Any]],
        context: Optional[str]
    ) -> str:
        """构建问题生成提示词"""
        prompt = f"请生成一个{interview_type}类型的面试问题，难度级别：{difficulty_level}。\n\n"

        if knowledge_results:
            prompt += "参考以下知识点：\n"
            for i, kr in enumerate(knowledge_results, 1):
                prompt += f"{i}. {kr['content']}\n"
            prompt += "\n"

        if context:
            prompt += f"上下文：{context}\n\n"

        if self.used_questions:
            prompt += f"请避免与以下已使用的问题重复：\n"
            for q in self.used_questions[-3:]:  # 只显示最近3个
                prompt += f"- {q}\n"
            prompt += "\n"

        prompt += "请直接输出问题，不需要额外说明。"

        return prompt

