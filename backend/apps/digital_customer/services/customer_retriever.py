"""
混合检索服务 - 结合 BM25 和 Embedding 进行语义检索
"""
from typing import List, Dict, Any
import numpy as np
from sqlalchemy.orm import Session
from rank_bm25 import BM25Okapi
import jieba
from loguru import logger

from backend.models.db_models import CustomerChunk, CustomerProfile
from backend.apps.customer_service.services.embedding_service import embedding_service


class CustomerRetriever:
    """客户画像知识混合检索服务"""

    # 混合检索权重
    BM25_WEIGHT = 0.6
    EMBEDDING_WEIGHT = 0.4

    def __init__(self, db: Session):
        self.db = db
        self._bm25_cache = {}  # {customer_profile_id: (bm25_model, chunks)}

    async def retrieve(
        self,
        customer_profile_id: int,
        query: str,
        top_k: int = 3,
        use_hybrid: bool = True
    ) -> List[Dict[str, Any]]:
        """
        混合检索相关文本块

        Args:
            customer_profile_id: 客户画像 ID
            query: 用户查询
            top_k: 返回前 K 个结果
            use_hybrid: 是否使用混合检索（False 则只用 Embedding）

        Returns:
            List[Dict]: [{"text": str, "score": float, "chunk_index": int}, ...]
        """
        # 1. 加载所有 chunks
        chunks = self.db.query(CustomerChunk).filter(
            CustomerChunk.customer_profile_id == customer_profile_id
        ).order_by(CustomerChunk.chunk_index).all()

        if not chunks:
            logger.warning(f"No chunks found for customer_profile_id={customer_profile_id}")
            return []

        # 2. BM25 检索
        bm25_scores = None
        if use_hybrid:
            bm25_scores = self._bm25_search(customer_profile_id, query, chunks)

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
        return results[:top_k]

    def _bm25_search(self, customer_profile_id: int, query: str, chunks: List[CustomerChunk]) -> np.ndarray:
        """BM25 关键词检索"""
        # 检查缓存
        if customer_profile_id not in self._bm25_cache:
            # 分词
            tokenized_corpus = [list(jieba.cut(chunk.chunk_text)) for chunk in chunks]
            bm25_model = BM25Okapi(tokenized_corpus)
            self._bm25_cache[customer_profile_id] = bm25_model

        bm25_model = self._bm25_cache[customer_profile_id]
        tokenized_query = list(jieba.cut(query))
        scores = bm25_model.get_scores(tokenized_query)

        # 归一化到 [0, 1]
        if scores.max() > 0:
            scores = scores / scores.max()

        return scores

    async def _embedding_search(self, query: str, chunks: List[CustomerChunk]) -> np.ndarray:
        """向量相似度检索"""
        # 生成查询向量
        query_embedding = embedding_service.get_embedding(query)

        # 计算余弦相似度
        similarities = []
        for chunk in chunks:
            if chunk.embedding:
                chunk_embedding = np.frombuffer(chunk.embedding, dtype=np.float32)
                similarity = np.dot(query_embedding, chunk_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(chunk_embedding)
                )
                similarities.append(similarity)
            else:
                similarities.append(0.0)

        return np.array(similarities)

    def _combine_scores(self, bm25_scores: np.ndarray, embedding_scores: np.ndarray) -> np.ndarray:
        """混合评分"""
        return self.BM25_WEIGHT * bm25_scores + self.EMBEDDING_WEIGHT * embedding_scores
