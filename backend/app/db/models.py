from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, Float, Boolean, LargeBinary
from backend.app.db.database import Base
import enum

class SourceType(str, enum.Enum):
    person = "person"   # 人物资料
    book = "book"       # 书籍内容
    topic = "topic"     # 专题课程

class KnowledgeSource(Base):
    """知识源表 - 存储名人/书籍/专题的结构化信息"""
    __tablename__ = "knowledge_sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    source_type = Column(String(20), nullable=False, default="person")
    author = Column(String(100), nullable=True)  # 书籍作者

    # 人物信息
    birth_year = Column(Integer, nullable=True)
    death_year = Column(Integer, nullable=True)
    nationality = Column(String(50), nullable=True)
    occupation = Column(String(100), nullable=True)

    # 内容信息
    biography = Column(Text, nullable=True)
    famous_works = Column(Text, nullable=True)
    famous_quotes = Column(Text, nullable=True)
    personality_traits = Column(Text, nullable=True)
    speech_style = Column(Text, nullable=True)

    # AI 相关
    system_prompt = Column(Text, nullable=True)
    knowledge_base = Column(Text, nullable=True)  # 检索用知识库（可选）
    raw_content = Column(Text, nullable=True)     # PDF 原始文本
    source_pdf_path = Column(String(500), nullable=True)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "source_type": self.source_type,
            "author": self.author,
            "birth_year": self.birth_year,
            "death_year": self.death_year,
            "nationality": self.nationality,
            "occupation": self.occupation,
            "biography": self.biography,
            "famous_works": self.famous_works,
            "famous_quotes": self.famous_quotes,
            "personality_traits": self.personality_traits,
            "speech_style": self.speech_style,
            "system_prompt": self.system_prompt,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class CustomerServiceQA(Base):
    """客服QA知识库表"""
    __tablename__ = "customer_service_qa"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_count = Column(Integer, nullable=True)  # 提问次数
    topic_name = Column(String(200), nullable=False, index=True)  # 主题名称
    typical_question = Column(Text, nullable=False)  # 典型提问
    standard_script = Column(Text, nullable=False)  # 标准话术(JSON格式)
    risk_notes = Column(Text, nullable=True)  # 风险注意事项
    keywords = Column(Text, nullable=True)  # 提取的关键词(用于BM25)
    embedding = Column(LargeBinary, nullable=True)  # 向量嵌入(numpy序列化)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "question_count": self.question_count,
            "topic_name": self.topic_name,
            "typical_question": self.typical_question,
            "standard_script": self.standard_script,
            "risk_notes": self.risk_notes,
            "keywords": self.keywords,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class CustomerServiceSession(Base):
    """客服会话记录表"""
    __tablename__ = "customer_service_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    message_count = Column(Integer, default=0)
    avg_confidence = Column(Float, nullable=True)
    transfer_to_human = Column(Boolean, default=False)
    user_rating = Column(Integer, nullable=True)  # 用户评分1-5

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "message_count": self.message_count,
            "avg_confidence": self.avg_confidence,
            "transfer_to_human": self.transfer_to_human,
            "user_rating": self.user_rating,
        }


class CustomerServiceLog(Base):
    """客服对话日志表"""
    __tablename__ = "customer_service_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), nullable=False, index=True)
    user_query = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    matched_qa_id = Column(Integer, nullable=True)
    match_type = Column(String(50), nullable=True)  # exact/semantic/no_match
    confidence_score = Column(Float, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_query": self.user_query,
            "bot_response": self.bot_response,
            "matched_qa_id": self.matched_qa_id,
            "match_type": self.match_type,
            "confidence_score": self.confidence_score,
            "response_time_ms": self.response_time_ms,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


class CSVRegistry(Base):
    """CSV 文件注册表 - 记录已导入的 CSV 文件，避免重复导入"""
    __tablename__ = "csv_registry"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), unique=True, nullable=False, index=True)  # 文件名
    file_hash = Column(String(64), nullable=False)  # MD5 哈希值
    record_count = Column(Integer, default=0)  # 导入的记录数
    status = Column(String(20), default="success")  # success/failed
    imported_at = Column(DateTime, default=datetime.utcnow)  # 导入时间

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "filename": self.filename,
            "file_hash": self.file_hash,
            "record_count": self.record_count,
            "status": self.status,
            "imported_at": self.imported_at.isoformat() if self.imported_at else None,
        }
