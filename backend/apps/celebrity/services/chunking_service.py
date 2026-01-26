"""
文本分块服务 - 智能分割长文本为语义单元
"""
from typing import List, Dict, Any
import re
from loguru import logger


class ChunkingService:
    """文本分块服务"""

    @staticmethod
    def chunk_text(
        text: str,
        chunk_size: int = 400,
        overlap: int = 50,
        min_chunk_size: int = 100
    ) -> List[Dict[str, Any]]:
        """
        智能分块文本

        Args:
            text: 原始文本
            chunk_size: 每块的目标字数
            overlap: 块之间的重叠字数
            min_chunk_size: 最小块大小（小于此大小的块会被合并）

        Returns:
            List[Dict]: [{"text": str, "metadata": dict}, ...]
        """
        if not text or not text.strip():
            return []

        # 1. 按双换行符分段（保留自然段落）
        paragraphs = re.split(r'\n\n+', text.strip())
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        chunks = []
        current_chunk = ""
        chunk_index = 0

        for para in paragraphs:
            para_len = len(para)

            # 如果当前段落本身就很长，需要切分
            if para_len > chunk_size:
                # 先保存之前积累的块
                if current_chunk:
                    chunks.append({
                        "text": current_chunk.strip(),
                        "chunk_index": chunk_index,
                        "metadata": {}
                    })
                    chunk_index += 1
                    current_chunk = ""

                # 对长段落进行切分
                sub_chunks = ChunkingService._split_long_paragraph(
                    para,
                    chunk_size=chunk_size,
                    overlap=overlap
                )
                for sub_chunk in sub_chunks:
                    chunks.append({
                        "text": sub_chunk.strip(),
                        "chunk_index": chunk_index,
                        "metadata": {}
                    })
                    chunk_index += 1

            # 如果加上这个段落后超过目标大小，先保存当前块
            elif len(current_chunk) + para_len > chunk_size:
                if current_chunk:
                    chunks.append({
                        "text": current_chunk.strip(),
                        "chunk_index": chunk_index,
                        "metadata": {}
                    })
                    chunk_index += 1

                    # 保留重叠部分
                    if overlap > 0 and len(current_chunk) > overlap:
                        current_chunk = current_chunk[-overlap:] + "\n\n" + para
                    else:
                        current_chunk = para
                else:
                    current_chunk = para

            # 否则，继续积累
            else:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para

        # 保存最后一个块
        if current_chunk and len(current_chunk.strip()) >= min_chunk_size:
            chunks.append({
                "text": current_chunk.strip(),
                "chunk_index": chunk_index,
                "metadata": {}
            })

        logger.info(f"文本分块完成: 原始长度 {len(text)} 字，生成 {len(chunks)} 个块")
        return chunks

    @staticmethod
    def _split_long_paragraph(
        paragraph: str,
        chunk_size: int = 400,
        overlap: int = 50
    ) -> List[str]:
        """
        分割长段落

        Args:
            paragraph: 长段落文本
            chunk_size: 目标块大小
            overlap: 重叠大小

        Returns:
            List[str]: 分割后的子块列表
        """
        # 尝试按句子分割
        sentences = re.split(r'([。！？；.!?;])', paragraph)

        # 重新组合句子（包含标点）
        sentences_with_punct = []
        for i in range(0, len(sentences) - 1, 2):
            if i + 1 < len(sentences):
                sentences_with_punct.append(sentences[i] + sentences[i + 1])
            else:
                sentences_with_punct.append(sentences[i])

        if not sentences_with_punct:
            # 如果分割失败，直接按字数硬切
            return ChunkingService._hard_split(paragraph, chunk_size, overlap)

        # 按句子组合成块
        sub_chunks = []
        current_sub_chunk = ""

        for sentence in sentences_with_punct:
            if len(current_sub_chunk) + len(sentence) > chunk_size:
                if current_sub_chunk:
                    sub_chunks.append(current_sub_chunk.strip())

                    # 添加重叠
                    if overlap > 0 and len(current_sub_chunk) > overlap:
                        current_sub_chunk = current_sub_chunk[-overlap:] + sentence
                    else:
                        current_sub_chunk = sentence
                else:
                    # 单句就超过大小，强制加入
                    sub_chunks.append(sentence.strip())
                    current_sub_chunk = ""
            else:
                current_sub_chunk += sentence

        if current_sub_chunk:
            sub_chunks.append(current_sub_chunk.strip())

        return sub_chunks

    @staticmethod
    def _hard_split(text: str, chunk_size: int, overlap: int) -> List[str]:
        """
        硬切分文本（按字数）

        Args:
            text: 文本
            chunk_size: 块大小
            overlap: 重叠大小

        Returns:
            List[str]: 分割后的块
        """
        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap if overlap > 0 else end

        return chunks


# 创建全局实例
chunking_service = ChunkingService()
