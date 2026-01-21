"""
QA匹配引擎 - 基于BM25和Embedding的混合匹配策略
实现三层匹配架构：
1. BM25关键词匹配（精准匹配）
2. Embedding余弦相似度（语义匹配）
3. 混合评分：score = 0.6*BM25 + 0.4*Embedding
"""
import os
import numpy as np
import jieba
from typing import List, Tuple, Optional
from rank_bm25 import BM25Okapi
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from backend.models.db_models import CustomerServiceQA
from .embedding_service import EmbeddingService


class QAMatcher:
    """QA匹配引擎"""

    def __init__(self, api_key: Optional[str] = None):
        self.qa_records: List[CustomerServiceQA] = []
        self.bm25: Optional[BM25Okapi] = None
        self.embeddings: List[np.ndarray] = []
        self.embedding_dim: int = 1536  # dashscope text-embedding-v2 维度
        self.is_loaded = False

        # 初始化embedding服务
        if not api_key:
            api_key = os.environ.get('DASHSCOPE_API_KEY')
        self.embedding_service = EmbeddingService(api_key=api_key)

        # 置信度阈值
        self.HIGH_CONFIDENCE_THRESHOLD = 0.9  # 高置信度：直接返回话术
        self.MID_CONFIDENCE_THRESHOLD = 0.6   # 中置信度：LLM改写
        # <0.6 为低置信度：转人工

        # 混合评分权重
        self.BM25_WEIGHT = 0.6
        self.EMBEDDING_WEIGHT = 0.4

    async def load_qa_data(self, db: AsyncSession):
        """从数据库加载QA数据并初始化BM25和Embedding索引"""
        logger.info("开始加载QA数据...")

        # 查询所有QA记录
        result = await db.execute(select(CustomerServiceQA))
        self.qa_records = result.scalars().all()

        if not self.qa_records:
            logger.warning("数据库中没有QA记录，请先导入数据")
            return

        logger.info(f"加载了 {len(self.qa_records)} 条QA记录")

        # 初始化BM25索引
        tokenized_keywords = []
        for qa in self.qa_records:
            if qa.keywords:
                # keywords已经是空格分隔的关键词字符串
                tokens = qa.keywords.split()
                tokenized_keywords.append(tokens)
            else:
                tokenized_keywords.append([])

        self.bm25 = BM25Okapi(tokenized_keywords)
        logger.info("BM25索引初始化完成")

        # 加载Embedding向量
        self.embeddings = []
        for qa in self.qa_records:
            if qa.embedding:
                # 从bytes反序列化为numpy数组
                vec = np.frombuffer(qa.embedding, dtype=np.float32)
                self.embeddings.append(vec)
            else:
                # 如果没有embedding，使用零向量
                if self.embedding_dim == 0 and len(self.embeddings) > 0:
                    self.embedding_dim = len(self.embeddings[0])
                zero_vec = np.zeros(self.embedding_dim if self.embedding_dim > 0 else 512, dtype=np.float32)
                self.embeddings.append(zero_vec)

        if self.embeddings:
            self.embedding_dim = len(self.embeddings[0])
            logger.info(f"Embedding向量加载完成，维度: {self.embedding_dim}")

        self.is_loaded = True
        logger.info("QA匹配引擎初始化完成")

    def _compute_bm25_scores(self, query: str) -> List[float]:
        """计算BM25分数"""
        if not self.bm25:
            return [0.0] * len(self.qa_records)

        # 对查询进行分词
        query_tokens = jieba.lcut(query)

        # 计算BM25分数
        scores = self.bm25.get_scores(query_tokens)

        # 归一化到[0, 1]
        max_score = max(scores) if max(scores) > 0 else 1.0
        normalized_scores = [s / max_score for s in scores]

        return normalized_scores

    def _compute_embedding_scores(self, query_embedding: np.ndarray) -> List[float]:
        """计算Embedding余弦相似度分数"""
        if not self.embeddings or len(query_embedding) == 0:
            return [0.0] * len(self.qa_records)

        scores = []
        query_norm = np.linalg.norm(query_embedding)

        if query_norm == 0:
            return [0.0] * len(self.qa_records)

        for emb in self.embeddings:
            emb_norm = np.linalg.norm(emb)
            if emb_norm == 0:
                scores.append(0.0)
            else:
                # 余弦相似度
                cosine_sim = np.dot(query_embedding, emb) / (query_norm * emb_norm)
                # 将[-1, 1]映射到[0, 1]
                normalized_sim = (cosine_sim + 1) / 2
                scores.append(float(normalized_sim))

        return scores

    def _generate_query_embedding(self, query: str) -> np.ndarray:
        """使用dashscope embedding API生成查询向量"""
        if not query or not query.strip():
            return np.zeros(self.embedding_dim, dtype=np.float32)

        try:
            # 调用embedding服务
            query_vec = self.embedding_service.get_embedding(query)
            return query_vec
        except Exception as e:
            logger.error(f"生成查询embedding失败: {e}")
            # 出错时返回零向量，BM25仍可正常工作
            return np.zeros(self.embedding_dim, dtype=np.float32)

    async def match(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Tuple[CustomerServiceQA, float, str]]:
        """
        匹配查询到最相关的QA记录

        Args:
            query: 用户查询
            top_k: 返回前k个结果

        Returns:
            List of (qa_record, confidence_score, match_type)
            match_type: 'high_confidence' | 'mid_confidence' | 'low_confidence'
        """
        if not self.is_loaded:
            logger.error("QA匹配引擎未初始化，请先调用load_qa_data")
            return []

        if not query.strip():
            return []

        logger.info(f"开始匹配查询: {query}")

        # 1. 计算BM25分数
        bm25_scores = self._compute_bm25_scores(query)

        # 2. 计算Embedding分数
        query_embedding = self._generate_query_embedding(query)
        embedding_scores = self._compute_embedding_scores(query_embedding)

        # 3. 混合评分
        mixed_scores = []
        for i in range(len(self.qa_records)):
            mixed_score = (
                self.BM25_WEIGHT * bm25_scores[i] +
                self.EMBEDDING_WEIGHT * embedding_scores[i]
            )
            mixed_scores.append(mixed_score)

        # 4. 排序并取Top K
        scored_records = list(zip(self.qa_records, mixed_scores, bm25_scores, embedding_scores))
        scored_records.sort(key=lambda x: x[1], reverse=True)
        top_records = scored_records[:top_k]

        # 5. 确定置信度类型
        results = []
        for qa, mixed_score, bm25_score, emb_score in top_records:
            if mixed_score >= self.HIGH_CONFIDENCE_THRESHOLD:
                match_type = 'high_confidence'
            elif mixed_score >= self.MID_CONFIDENCE_THRESHOLD:
                match_type = 'mid_confidence'
            else:
                match_type = 'low_confidence'

            logger.info(
                f"匹配结果: {qa.topic_name} | "
                f"混合分数: {mixed_score:.3f} | "
                f"BM25: {bm25_score:.3f} | "
                f"Embedding: {emb_score:.3f} | "
                f"类型: {match_type}"
            )

            results.append((qa, mixed_score, match_type))

        return results

    def should_transfer_to_human(self, query: str, top_match: Optional[Tuple[CustomerServiceQA, float, str]]) -> bool:
        """
        判断是否应该转人工客服

        条件：
        1. 用户明确要求："人工"、"转人工"、"客服"
        2. 用户表达不满

        注意：
        - risk_notes 是回复时的上下文提示，不作为转人工依据
        - 低置信度时会引导用户重新描述问题，而不是直接转人工
        """
        # 条件1: 用户明确要求
        transfer_keywords = ['人工', '转人工', '客服', '真人', '人工客服', '转接']
        if any(keyword in query for keyword in transfer_keywords):
            logger.info("用户明确要求转人工")
            return True

        # 条件2: 用户表达不满
        dissatisfaction_keywords = ['不满意', '投诉', '差评', '退款', '不行', '太差', '垃圾']
        if any(keyword in query for keyword in dissatisfaction_keywords):
            logger.info("检测到用户不满情绪")
            return True

        return False

    def get_stats(self) -> dict:
        """获取匹配引擎统计信息"""
        return {
            'total_qa_records': len(self.qa_records),
            'embedding_dim': self.embedding_dim,
            'is_loaded': self.is_loaded,
            'high_confidence_threshold': self.HIGH_CONFIDENCE_THRESHOLD,
            'mid_confidence_threshold': self.MID_CONFIDENCE_THRESHOLD,
            'bm25_weight': self.BM25_WEIGHT,
            'embedding_weight': self.EMBEDDING_WEIGHT
        }
