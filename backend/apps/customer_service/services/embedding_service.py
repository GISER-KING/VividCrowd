"""
Embedding服务 - 使用dashscope embedding API生成文本向量
支持单条和批量文本向量化
"""
import numpy as np
from typing import List, Optional
from dashscope import TextEmbedding
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


class EmbeddingService:
    """使用dashscope text-embedding API的向量服务"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.model = 'text-embedding-v2'  # 阿里云通用文本向量模型
        self.dimension = 1536  # v2模型输出维度
        self.batch_size = 25  # dashscope批量限制

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True
    )
    def get_embedding(self, text: str) -> np.ndarray:
        """
        获取单个文本的向量

        Args:
            text: 输入文本

        Returns:
            1536维的numpy向量
        """
        if not text or not text.strip():
            return np.zeros(self.dimension, dtype=np.float32)

        try:
            response = TextEmbedding.call(
                model=self.model,
                input=text,
                api_key=self.api_key
            )

            if response.status_code == 200:
                embedding = response.output['embeddings'][0]['embedding']
                return np.array(embedding, dtype=np.float32)
            else:
                logger.error(f"Embedding API错误: {response.code} - {response.message}")
                return np.zeros(self.dimension, dtype=np.float32)

        except Exception as e:
            logger.error(f"Embedding调用异常: {e}")
            raise

    def get_embeddings_batch(self, texts: List[str]) -> List[np.ndarray]:
        """
        批量获取文本向量

        Args:
            texts: 文本列表

        Returns:
            向量列表
        """
        if not texts:
            return []

        results = []
        # 分批处理，每批最多25条
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            batch_results = self._process_batch(batch)
            results.extend(batch_results)
            logger.info(f"已处理 {min(i + self.batch_size, len(texts))}/{len(texts)} 条文本的embedding")

        return results

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True
    )
    def _process_batch(self, texts: List[str]) -> List[np.ndarray]:
        """处理单个批次的文本"""
        # 过滤空文本，记录索引
        valid_texts = []
        valid_indices = []
        for i, text in enumerate(texts):
            if text and text.strip():
                valid_texts.append(text)
                valid_indices.append(i)

        # 初始化结果（全部为零向量）
        results = [np.zeros(self.dimension, dtype=np.float32) for _ in texts]

        if not valid_texts:
            return results

        try:
            response = TextEmbedding.call(
                model=self.model,
                input=valid_texts,
                api_key=self.api_key
            )

            if response.status_code == 200:
                embeddings = response.output['embeddings']
                for j, emb_data in enumerate(embeddings):
                    original_idx = valid_indices[j]
                    results[original_idx] = np.array(emb_data['embedding'], dtype=np.float32)
            else:
                logger.error(f"批量Embedding API错误: {response.code} - {response.message}")

        except Exception as e:
            logger.error(f"批量Embedding调用异常: {e}")
            raise

        return results

    def embedding_to_bytes(self, embedding: np.ndarray) -> bytes:
        """将numpy向量序列化为bytes"""
        return embedding.astype(np.float32).tobytes()

    def bytes_to_embedding(self, data: bytes) -> np.ndarray:
        """将bytes反序列化为numpy向量"""
        return np.frombuffer(data, dtype=np.float32)


# 创建全局实例（延迟初始化避免循环导入）
def _get_embedding_service():
    from backend.core.config import settings
    return EmbeddingService(api_key=settings.DASHSCOPE_API_KEY)

embedding_service = _get_embedding_service()
