"""
Excel/CSV数据导入服务
负责将QA知识库数据从CSV文件导入到数据库，并生成BM25关键词和向量嵌入
"""
import csv
import json
import re
import os
from typing import List, Optional
from datetime import datetime
import numpy as np
import jieba
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from loguru import logger

from backend.models.db_models import CustomerServiceQA
from .embedding_service import EmbeddingService


# 停用词列表（常见的无意义词汇）
STOP_WORDS = {
    '的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
    '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好',
    '自己', '这', '那', '什么', '能', '可以', '吗', '呢', '啊', '吧', '呀', '嘛',
    '哦', '哪', '怎么', '怎样', '如何', '为什么', '这个', '那个', '这些', '那些',
    '请问', '老师', '您好', '谢谢', '请', '还', '又', '把', '被', '让', '给', '对',
    '从', '向', '但', '但是', '如果', '虽然', '因为', '所以', '或者', '而且',
}


def extract_keywords(text: str, top_n: int = 20) -> str:
    """
    使用jieba分词提取关键词，用于BM25检索

    Args:
        text: 输入文本
        top_n: 保留前N个关键词

    Returns:
        空格分隔的关键词字符串
    """
    if not text:
        return ""

    # jieba分词
    words = jieba.lcut(text)

    # 过滤：去除停用词、单字符、纯数字、标点
    filtered_words = []
    for word in words:
        word = word.strip()
        if len(word) < 2:
            continue
        if word in STOP_WORDS:
            continue
        if word.isdigit():
            continue
        if re.match(r'^[^\w\u4e00-\u9fff]+$', word):
            continue
        filtered_words.append(word)

    # 词频统计
    word_freq = {}
    for word in filtered_words:
        word_freq[word] = word_freq.get(word, 0) + 1

    # 按频率排序取Top N
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    top_words = [w[0] for w in sorted_words[:top_n]]

    return ' '.join(top_words)


def parse_csv_row(row: List[str]) -> dict:
    """
    解析CSV行数据

    Args:
        row: CSV行，包含5个字段

    Returns:
        解析后的字典
    """
    # CSV格式：提问次数, 主题名称, 典型提问, 标准话术, 风险注意事项
    result = {
        'question_count': None,
        'topic_name': '',
        'typical_question': '',
        'standard_script': '',
        'risk_notes': None,
    }

    if len(row) >= 1 and row[0].strip():
        try:
            result['question_count'] = int(row[0].strip())
        except ValueError:
            pass

    if len(row) >= 2:
        result['topic_name'] = row[1].strip()

    if len(row) >= 3:
        result['typical_question'] = row[2].strip()

    if len(row) >= 4:
        result['standard_script'] = row[3].strip()

    if len(row) >= 5 and row[4].strip():
        result['risk_notes'] = row[4].strip()

    return result


async def import_qa_from_csv(
    db: AsyncSession,
    csv_path: str,
    clear_existing: bool = True,
    api_key: Optional[str] = None
) -> dict:
    """
    从CSV文件导入QA数据到数据库

    Args:
        db: 数据库会话
        csv_path: CSV文件路径
        clear_existing: 是否清空现有数据
        api_key: dashscope API key，用于生成embedding

    Returns:
        导入结果统计
    """
    logger.info(f"开始导入CSV文件: {csv_path}")

    # 获取API key
    if not api_key:
        api_key = os.environ.get('DASHSCOPE_API_KEY')

    if not api_key:
        return {'success': False, 'message': '缺少DASHSCOPE_API_KEY', 'count': 0}

    # 读取CSV
    rows = []
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        header = next(reader, None)  # 跳过表头
        for row in reader:
            if row and any(cell.strip() for cell in row):  # 跳过空行
                rows.append(row)

    logger.info(f"读取到 {len(rows)} 条有效数据")

    if not rows:
        return {'success': False, 'message': 'CSV文件为空', 'count': 0}

    # 清空现有数据
    if clear_existing:
        await db.execute(delete(CustomerServiceQA))
        await db.commit()
        logger.info("已清空现有QA数据")

    # 解析数据
    parsed_data = []
    for row in rows:
        data = parse_csv_row(row)
        if data['topic_name'] and data['typical_question']:
            parsed_data.append(data)

    logger.info(f"解析有效记录 {len(parsed_data)} 条")

    # 使用dashscope embedding服务
    embedding_service = EmbeddingService(api_key=api_key)
    embedding_dim = embedding_service.dimension  # 1536

    # 准备文本列表用于批量生成embedding
    all_texts = [d['typical_question'] + ' ' + d['topic_name'] for d in parsed_data]

    # 批量生成embedding
    logger.info("开始生成embedding向量...")
    embeddings = embedding_service.get_embeddings_batch(all_texts)
    logger.info(f"Embedding生成完成，维度: {embedding_dim}")

    # 插入数据
    success_count = 0
    error_count = 0

    for i, data in enumerate(parsed_data):
        try:
            # 提取关键词
            text_for_keywords = data['typical_question'] + ' ' + data['topic_name']
            keywords = extract_keywords(text_for_keywords)

            # 序列化embedding
            embedding_bytes = embedding_service.embedding_to_bytes(embeddings[i])

            # 创建记录
            qa_record = CustomerServiceQA(
                question_count=data['question_count'],
                topic_name=data['topic_name'],
                typical_question=data['typical_question'],
                standard_script=data['standard_script'],
                risk_notes=data['risk_notes'],
                keywords=keywords,
                embedding=embedding_bytes,
                created_at=datetime.utcnow()
            )
            db.add(qa_record)
            success_count += 1

        except Exception as e:
            logger.error(f"插入记录失败: {e}, 数据: {data}")
            error_count += 1

    await db.commit()

    result = {
        'success': True,
        'message': f'导入完成',
        'total_rows': len(rows),
        'parsed_count': len(parsed_data),
        'success_count': success_count,
        'error_count': error_count,
        'embedding_dim': embedding_dim
    }

    logger.info(f"导入完成: {result}")
    return result


async def get_qa_count(db: AsyncSession) -> int:
    """获取QA记录总数"""
    result = await db.execute(select(CustomerServiceQA))
    return len(result.scalars().all())


async def get_all_qa(db: AsyncSession) -> List[CustomerServiceQA]:
    """获取所有QA记录"""
    result = await db.execute(select(CustomerServiceQA))
    return result.scalars().all()
