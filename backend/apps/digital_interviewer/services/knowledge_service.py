"""
面试知识库服务 - 管理题库和RAG检索
"""
import numpy as np
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from openai import AsyncOpenAI

from backend.models.db_models import InterviewKnowledge


class InterviewKnowledgeService:
    """面试知识库服务"""

    def __init__(self, db: Session, api_key: str = None, base_url: str = None):
        """初始化知识库服务"""
        self.db = db
        self.client = AsyncOpenAI(
            api_key=api_key or "sk-xxx",
            base_url=base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        self.embedding_model = "text-embedding-v3"

    async def add_knowledge(
        self,
        interview_type: str,
        content: str,
        category: str = None,
        difficulty_level: str = None,
        source_filename: str = None
    ) -> InterviewKnowledge:
        """
        添加知识条目

        Args:
            interview_type: 面试类型
            content: 内容
            category: 类别
            difficulty_level: 难度
            source_filename: 来源文件

        Returns:
            知识条目对象
        """
        # 生成embedding
        embedding = await self._generate_embedding(content)

        # 创建知识条目
        knowledge = InterviewKnowledge(
            interview_type=interview_type,
            category=category,
            content=content,
            difficulty_level=difficulty_level,
            source_filename=source_filename,
            embedding=embedding.tobytes() if embedding is not None else None
        )

        self.db.add(knowledge)
        self.db.commit()
        self.db.refresh(knowledge)

        return knowledge

    async def search_knowledge(
        self,
        query: str,
        interview_type: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        检索相关知识

        Args:
            query: 查询文本
            interview_type: 面试类型
            top_k: 返回数量

        Returns:
            相关知识列表
        """
        # 生成查询embedding
        query_embedding = await self._generate_embedding(query)
        if query_embedding is None:
            return []

        # 获取该类型的所有知识
        knowledge_items = self.db.query(InterviewKnowledge).filter_by(
            interview_type=interview_type
        ).all()

        if not knowledge_items:
            return []

        # 计算相似度
        results = []
        for item in knowledge_items:
            if item.embedding:
                item_embedding = np.frombuffer(item.embedding, dtype=np.float32)
                similarity = self._cosine_similarity(query_embedding, item_embedding)
                results.append({
                    "content": item.content,
                    "category": item.category,
                    "difficulty_level": item.difficulty_level,
                    "similarity": float(similarity)
                })

        # 排序并返回top_k
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]

    async def _generate_embedding(self, text: str) -> Optional[np.ndarray]:
        """生成文本embedding"""
        try:
            response = await self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            embedding = np.array(response.data[0].embedding, dtype=np.float32)
            return embedding
        except Exception as e:
            print(f"生成embedding失败: {e}")
            return None

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """计算余弦相似度"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot_product / (norm1 * norm2)

