import os
import fitz  # PyMuPDF
import openpyxl
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from loguru import logger
import numpy as np

from backend.models.db_models import SalesKnowledge
from backend.apps.customer_service.services.embedding_service import EmbeddingService
from backend.apps.digital_customer.services.chunking_service import chunking_service

class SalesKnowledgeService:
    """销售知识库服务 - 处理文件导入和RAG检索"""

    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = EmbeddingService()

    async def import_file(self, file_path: str, filename: str):
        """导入文件到知识库"""
        ext = filename.split('.')[-1].lower()
        
        items = []
        if ext == 'pdf':
            items = self._parse_pdf(file_path)
        else:
            raise ValueError("不支持的文件格式，仅支持 pdf")

        if not items:
            logger.warning(f"No content extracted from {filename}")
            return 0

        # 批量生成 Embedding
        texts = [item['content'] for item in items]
        logger.info(f"Generating embeddings for {len(texts)} items from {filename}...")
        embeddings = self.embedding_service.get_embeddings_batch(texts)

        # 保存到数据库
        count = 0
        for item, embedding in zip(items, embeddings):
            record = SalesKnowledge(
                stage=item.get('stage'),
                category=item.get('category', 'general'),
                content=item['content'],
                source_filename=filename,
                embedding=embedding.tobytes()
            )
            self.db.add(record)
            count += 1
        
        self.db.commit()
        logger.info(f"Successfully imported {count} items from {filename}")
        return count

    def _parse_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """解析 PDF 文件"""
        items = []
        try:
            doc = fitz.open(file_path)
            full_text = ""
            for page in doc:
                full_text += page.get_text() + "\n"
            
            # 使用分块服务进行切分
            chunks = chunking_service.chunk_text(
                text=full_text,
                chunk_size=300,
                overlap=50
            )
            
            for chunk in chunks:
                items.append({
                    'content': chunk['text'],
                    'category': 'document',
                    # PDF 很难自动判断阶段，默认为 None
                })
                
        except Exception as e:
            logger.error(f"Error parsing PDF {file_path}: {e}")
            raise e
            
        return items

    async def search_knowledge(self, query: str, stage: int = None, limit: int = 3) -> List[str]:
        """检索相关知识"""
        query_embedding = self.embedding_service.get_embedding(query)
        
        # 由于 SQLite 不支持向量原生搜索，这里加载所有相关阶段的向量进行计算
        # 生产环境应使用 pgvector 或其他向量数据库
        query_stmt = self.db.query(SalesKnowledge)
        if stage:
            query_stmt = query_stmt.filter(SalesKnowledge.stage == stage)
            
        candidates = query_stmt.all()
        
        if not candidates:
            # 如果当前阶段没数据，尝试搜索所有阶段
            candidates = self.db.query(SalesKnowledge).all()
            
        if not candidates:
            return []
            
        scores = []
        for cand in candidates:
            if not cand.embedding:
                continue
            cand_vec = np.frombuffer(cand.embedding, dtype=np.float32)
            # 计算余弦相似度
            score = np.dot(query_embedding, cand_vec) / (np.linalg.norm(query_embedding) * np.linalg.norm(cand_vec))
            scores.append((score, cand.content))
            
        # 排序并返回前N个
        scores.sort(key=lambda x: x[1], reverse=True)
        return [item[1] for item in scores[:limit]]