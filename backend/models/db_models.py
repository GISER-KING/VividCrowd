from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, LargeBinary, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.core.database import Base
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


class CelebrityChunk(Base):
    """名人知识分块表 - 存储文档分块和向量嵌入"""
    __tablename__ = "celebrity_chunks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    knowledge_source_id = Column(Integer, ForeignKey("knowledge_sources.id", ondelete="CASCADE"), nullable=False, index=True)

    # 分块内容
    chunk_text = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)  # 在文档中的顺序
    chunk_metadata = Column(JSON, nullable=True)  # {"page": 1, "section": "第一章"}

    # 向量嵌入
    embedding = Column(LargeBinary, nullable=True)  # 存储序列化的 numpy array (1536维)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    knowledge_source = relationship("KnowledgeSource", backref="chunks")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "knowledge_source_id": self.knowledge_source_id,
            "chunk_text": self.chunk_text,
            "chunk_index": self.chunk_index,
            "chunk_metadata": self.chunk_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
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


class SalesKnowledge(Base):
    """销售培训知识库表 - 存储RAG用的销售知识"""
    __tablename__ = "sales_knowledge"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stage = Column(Integer, nullable=True)  # 适用阶段 (1-5)
    category = Column(String(50), nullable=True)  # 类别: script/qa/sop/product
    content = Column(Text, nullable=False)  # 文本内容
    source_filename = Column(String(255), nullable=True)  # 来源文件名
    embedding = Column(LargeBinary, nullable=True)  # 向量嵌入
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "stage": self.stage,
            "category": self.category,
            "content": self.content,
            "source_filename": self.source_filename,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ChatSession(Base):
    """对话会话表 - Celebrity应用的会话管理"""
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), unique=True, index=True, nullable=False)
    user_id = Column(String(64), nullable=True)  # 可选：用户标识
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # 关联的消息
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
        }


class ChatMessage(Base):
    """对话消息表 - Celebrity应用的消息记录"""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    sender = Column(String(100), nullable=False)  # "用户" 或 专家名字
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # 关联的会话
    session = relationship("ChatSession", back_populates="messages")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "sender": self.sender,
            "content": self.content,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


# ==================== 数字客户模型 ====================

class CustomerProfileRegistry(Base):
    """客户画像文件注册表 - 记录已导入的文件，避免重复导入"""
    __tablename__ = "customer_profile_registry"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), unique=True, nullable=False, index=True)  # 文件名
    file_hash = Column(String(64), nullable=False)  # MD5 哈希值
    customer_profile_id = Column(Integer, nullable=True)  # 关联的客户画像ID
    customer_name = Column(String(100), nullable=True)  # 客户姓名（冗余）
    customer_profile_type = Column(String(100), nullable=True)  # 客户画像类型（冗余）
    status = Column(String(20), default="success")  # success/failed
    imported_at = Column(DateTime, default=datetime.utcnow)  # 导入时间

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "filename": self.filename,
            "file_hash": self.file_hash,
            "customer_profile_id": self.customer_profile_id,
            "customer_name": self.customer_name,
            "customer_profile_type": self.customer_profile_type,
            "status": self.status,
            "imported_at": self.imported_at.isoformat() if self.imported_at else None,
        }


class CustomerProfile(Base):
    """客户画像表 - 存储标准客户的结构化信息"""
    __tablename__ = "customer_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=True, index=True)  # 真实客户姓名（可选）
    profile_type = Column(String(100), nullable=False, index=True)  # 客户画像类型（必填）

    # 客户基本信息
    age_range = Column(String(50), nullable=True)  # 年龄段
    gender = Column(String(20), nullable=True)
    occupation = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)

    # 客户特征
    personality_traits = Column(Text, nullable=True)  # 性格特征
    communication_style = Column(Text, nullable=True)  # 沟通风格
    pain_points = Column(Text, nullable=True)  # 痛点
    needs = Column(Text, nullable=True)  # 需求
    objections = Column(Text, nullable=True)  # 常见异议

    # AI 相关
    system_prompt = Column(Text, nullable=True)
    raw_content = Column(Text, nullable=True)  # 原始文本
    source_file_path = Column(String(500), nullable=True)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "profile_type": self.profile_type,
            "age_range": self.age_range,
            "gender": self.gender,
            "occupation": self.occupation,
            "industry": self.industry,
            "personality_traits": self.personality_traits,
            "communication_style": self.communication_style,
            "pain_points": self.pain_points,
            "needs": self.needs,
            "objections": self.objections,
            "system_prompt": self.system_prompt,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class CustomerChunk(Base):
    """客户知识分块表 - 存储文档分块和向量嵌入"""
    __tablename__ = "customer_chunks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_profile_id = Column(Integer, ForeignKey("customer_profiles.id"), nullable=False, index=True)

    # 冗余字段 - 避免级联删除问题
    customer_name = Column(String(100), nullable=True)  # 客户姓名
    customer_profile_type = Column(String(100), nullable=True)  # 客户画像类型

    # 分块内容
    chunk_text = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    chunk_metadata = Column(JSON, nullable=True)

    # 向量嵌入
    embedding = Column(LargeBinary, nullable=True)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    customer_profile = relationship("CustomerProfile", backref="chunks")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "customer_profile_id": self.customer_profile_id,
            "customer_name": self.customer_name,
            "customer_profile_type": self.customer_profile_type,
            "chunk_text": self.chunk_text,
            "chunk_index": self.chunk_index,
            "chunk_metadata": self.chunk_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ==================== 销售培训评价模型 ====================

class TrainingSession(Base):
    """培训会话表 - 记录每次培训的完整过程"""
    __tablename__ = "training_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), unique=True, nullable=False, index=True)

    # 关联信息
    trainee_id = Column(String(100), nullable=True)
    trainee_name = Column(String(100), nullable=True)
    customer_profile_id = Column(Integer, ForeignKey("customer_profiles.id"), nullable=False)

    # 冗余字段 - 避免级联删除问题
    customer_name = Column(String(100), nullable=True)  # 客户姓名
    customer_profile_type = Column(String(100), nullable=True)  # 客户画像类型
    customer_occupation = Column(String(100), nullable=True)  # 职业
    customer_industry = Column(String(100), nullable=True)  # 行业

    # 会话状态
    current_stage = Column(Integer, default=1)
    current_round = Column(Integer, default=0)
    total_rounds = Column(Integer, default=0)
    status = Column(String(20), default="in_progress")  # in_progress/completed/abandoned

    # 时间记录
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    customer_profile = relationship("CustomerProfile")

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "trainee_id": self.trainee_id,
            "trainee_name": self.trainee_name,
            "customer_profile_id": self.customer_profile_id,
            "customer_name": self.customer_name,
            "customer_profile_type": self.customer_profile_type,
            "customer_occupation": self.customer_occupation,
            "customer_industry": self.customer_industry,
            "current_stage": self.current_stage,
            "current_round": self.current_round,
            "total_rounds": self.total_rounds,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ConversationRound(Base):
    """对话轮次表 - 记录每一轮对话"""
    __tablename__ = "conversation_rounds"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("training_sessions.id"), nullable=False)

    round_number = Column(Integer, nullable=False)
    stage = Column(Integer, nullable=False)

    # 对话内容
    trainee_message = Column(Text, nullable=False)
    customer_response = Column(Text, nullable=False)

    # 实时分析
    detected_quality = Column(String(50), nullable=True)
    analysis_data = Column(JSON, nullable=True)

    timestamp = Column(DateTime, default=datetime.utcnow)

    # 关系
    session = relationship("TrainingSession", backref="rounds")

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "round_number": self.round_number,
            "stage": self.stage,
            "trainee_message": self.trainee_message,
            "customer_response": self.customer_response,
            "detected_quality": self.detected_quality,
            "analysis_data": self.analysis_data,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


class StageEvaluation(Base):
    """阶段评价表 - 记录每个阶段的完成情况"""
    __tablename__ = "stage_evaluations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("training_sessions.id"), nullable=False)

    stage_number = Column(Integer, nullable=False)
    stage_name = Column(String(100), nullable=True)

    # 任务完成度
    task_completed = Column(Boolean, default=False)
    completion_quality = Column(String(50), nullable=True)

    # 详细评价
    strengths = Column(JSON, nullable=True)
    weaknesses = Column(JSON, nullable=True)
    suggestions = Column(JSON, nullable=True)

    # 评分
    score = Column(Integer, nullable=True)

    # 时间记录
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    rounds_used = Column(Integer, nullable=True)

    # 关系
    session = relationship("TrainingSession", backref="stage_evaluations")

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "stage_number": self.stage_number,
            "stage_name": self.stage_name,
            "task_completed": self.task_completed,
            "completion_quality": self.completion_quality,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "suggestions": self.suggestions,
            "score": self.score,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "rounds_used": self.rounds_used,
        }


class FinalEvaluation(Base):
    """最终评价表 - 整体评价报告"""
    __tablename__ = "final_evaluations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("training_sessions.id"), unique=True, nullable=False)

    # 5项核心任务评分
    trust_building_score = Column(Integer, nullable=True)
    needs_diagnosis_score = Column(Integer, nullable=True)
    value_presentation_score = Column(Integer, nullable=True)
    objection_handling_score = Column(Integer, nullable=True)
    progress_management_score = Column(Integer, nullable=True)

    # 总分和等级
    total_score = Column(Integer, nullable=True)
    performance_level = Column(String(20), nullable=True)

    # 详细分析
    overall_strengths = Column(JSON, nullable=True)
    overall_weaknesses = Column(JSON, nullable=True)
    key_improvements = Column(JSON, nullable=True)

    # 具体指标
    uncompleted_tasks = Column(JSON, nullable=True)

    # 报告内容
    detailed_report = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    session = relationship("TrainingSession", backref="final_evaluation", uselist=False)

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "trust_building_score": self.trust_building_score,
            "needs_diagnosis_score": self.needs_diagnosis_score,
            "value_presentation_score": self.value_presentation_score,
            "objection_handling_score": self.objection_handling_score,
            "progress_management_score": self.progress_management_score,
            "total_score": self.total_score,
            "performance_level": self.performance_level,
            "overall_strengths": self.overall_strengths,
            "overall_weaknesses": self.overall_weaknesses,
            "key_improvements": self.key_improvements,
            "uncompleted_tasks": self.uncompleted_tasks,
            "detailed_report": self.detailed_report,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
