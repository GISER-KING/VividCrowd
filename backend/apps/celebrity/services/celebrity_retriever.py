"""
混合检索服务 - 结合 BM25 和 Embedding 进行语义检索
"""
from typing import List, Dict, Any, Optional
import numpy as np
from sqlalchemy.orm import Session
from rank_bm25 import BM25Okapi
import jieba
from loguru import logger

from backend.models.db_models import CelebrityChunk, KnowledgeSource
from backend.apps.customer_service.services.embedding_service import embedding_service


class CelebrityRetriever:
    """名人知识混合检索服务"""

    # 混合检索权重
    BM25_WEIGHT = 0.6
    EMBEDDING_WEIGHT = 0.4

    def __init__(self, db: Session):
        self.db = db
        self._bm25_cache = {}  # {knowledge_source_id: (bm25_model, chunks)}

    async def retrieve(
        self,
        knowledge_source_id: int,
        query: str,
        top_k: int = 3,
        use_hybrid: bool = True
    ) -> List[Dict[str, Any]]:
        """
        混合检索相关文本块

        Args:
            knowledge_source_id: 知识源 ID
            query: 用户查询
            top_k: 返回前 K 个结果
            use_hybrid: 是否使用混合检索（False 则只用 Embedding）

        Returns:
            List[Dict]: [{"text": str, "score": float, "chunk_index": int}, ...]
        """
        # 1. 加载所有 chunks
        chunks = self.db.query(CelebrityChunk).filter(
            CelebrityChunk.knowledge_source_id == knowledge_source_id
        ).order_by(CelebrityChunk.chunk_index).all()

        if not chunks:
            logger.warning(f"No chunks found for knowledge_source_id={knowledge_source_id}")
            return []

        # 2. BM25 检索
        bm25_scores = None
        if use_hybrid:
            bm25_scores = self._bm25_search(knowledge_source_id, query, chunks)

        # 3. Embedding 检索
        embedding_scores = await self._embedding_search(query, chunks)

        # 4. 混合评分
        if use_hybrid and bm25_scores is not None:
            final_scores = self._combine_scores(bm25_scores, embedding_scores)
        else:
            final_scores = embedding_scores

        # 5. 排序并返回 Top-K
        results = []
        for idx, score in enumerate(final_scores):
            results.append({
                "text": chunks[idx].chunk_text,
                "score": float(score),
                "chunk_index": chunks[idx].chunk_index,
                "metadata": chunks[idx].chunk_metadata
            })

        # 按分数降序排序
        results.sort(key=lambda x: x["score"], reverse=True)

        logger.info(
            f"Retrieved {len(results[:top_k])} chunks for query='{query[:30]}...' "
            f"(hybrid={use_hybrid})"
        )

        return results[:top_k]

    def _bm25_search(
        self,
        knowledge_source_id: int,
        query: str,
        chunks: List[CelebrityChunk]
    ) -> np.ndarray:
        """
        BM25 关键词检索

        Args:
            knowledge_source_id: 知识源 ID
            query: 查询文本
            chunks: 文本块列表

        Returns:
            np.ndarray: BM25 分数数组
        """
        # 检查缓存
        if knowledge_source_id not in self._bm25_cache:
            # 分词并构建 BM25 索引
            tokenized_corpus = [
                list(jieba.cut(chunk.chunk_text)) for chunk in chunks
            ]
            bm25_model = BM25Okapi(tokenized_corpus)
            self._bm25_cache[knowledge_source_id] = (bm25_model, chunks)
            logger.info(f"Built BM25 index for knowledge_source_id={knowledge_source_id}")
        else:
            bm25_model, _ = self._bm25_cache[knowledge_source_id]

        # 查询分词
        tokenized_query = list(jieba.cut(query))

        # 计算 BM25 分数
        bm25_scores = bm25_model.get_scores(tokenized_query)

        # 归一化到 [0, 1]
        if bm25_scores.max() > 0:
            bm25_scores = bm25_scores / bm25_scores.max()

        return bm25_scores

    async def _embedding_search(
        self,
        query: str,
        chunks: List[CelebrityChunk]
    ) -> np.ndarray:
        """
        Embedding 语义检索

        Args:
            query: 查询文本
            chunks: 文本块列表

        Returns:
            np.ndarray: 余弦相似度分数数组
        """
        # 1. 生成查询向量
        query_embedding = await embedding_service.get_embedding(query)

        # 2. 计算与所有 chunks 的余弦相似度
        similarities = []
        for chunk in chunks:
            if chunk.embedding is None:
                logger.warning(f"Chunk {chunk.id} has no embedding, skipping")
                similarities.append(0.0)
                continue

            # 反序列化向量
            chunk_embedding = np.frombuffer(chunk.embedding, dtype=np.float32)

            # 计算余弦相似度
            similarity = self._cosine_similarity(query_embedding, chunk_embedding)
            similarities.append(similarity)

        return np.array(similarities)

    @staticmethod
    def _cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        计算余弦相似度

        Args:
            vec1: 向量1
            vec2: 向量2

        Returns:
            float: 余弦相似度 [-1, 1]
        """
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def _combine_scores(
        self,
        bm25_scores: np.ndarray,
        embedding_scores: np.ndarray
    ) -> np.ndarray:
        """
        混合 BM25 和 Embedding 分数

        Args:
            bm25_scores: BM25 分数数组
            embedding_scores: Embedding 分数数组

        Returns:
            np.ndarray: 混合分数数组
        """
        # 确保 embedding_scores 在 [0, 1] 范围内
        # 余弦相似度范围是 [-1, 1]，需要归一化到 [0, 1]
        embedding_scores_normalized = (embedding_scores + 1) / 2

        # 加权求和
        combined = (
            self.BM25_WEIGHT * bm25_scores +
            self.EMBEDDING_WEIGHT * embedding_scores_normalized
        )

        return combined

    def clear_cache(self, knowledge_source_id: Optional[int] = None):
        """
        清除 BM25 缓存

        Args:
            knowledge_source_id: 指定清除某个知识源的缓存，None 则清除全部
        """
        if knowledge_source_id is None:
            self._bm25_cache.clear()
            logger.info("Cleared all BM25 cache")
        elif knowledge_source_id in self._bm25_cache:
            del self._bm25_cache[knowledge_source_id]
            logger.info(f"Cleared BM25 cache for knowledge_source_id={knowledge_source_id}")

    async def get_context_for_query(
        self,
        knowledge_source_id: int,
        query: str,
        top_k: int = 3,
        use_hybrid: bool = True
    ) -> str:
        """
        获取查询相关的上下文文本（用于拼接到 prompt）

        Args:
            knowledge_source_id: 知识源 ID
            query: 用户查询
            top_k: 返回前 K 个结果
            use_hybrid: 是否使用混合检索

        Returns:
            str: 拼接后的上下文文本
        """
        results = await self.retrieve(
            knowledge_source_id=knowledge_source_id,
            query=query,
            top_k=top_k,
            use_hybrid=use_hybrid
        )

        if not results:
            return ""

        # 拼接文本，添加分隔符
        context_parts = []
        for idx, result in enumerate(results, 1):
            context_parts.append(f"[相关内容 {idx}]\n{result['text']}")

        return "\n\n".join(context_parts)


# 创建全局实例（需要在使用时传入 db session）
def get_celebrity_retriever(db: Session) -> CelebrityRetriever:
    """获取 CelebrityRetriever 实例"""
    return CelebrityRetriever(db)
