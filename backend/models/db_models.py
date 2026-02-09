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


class CopilotMessage(Base):
    """销售助手对话记录表 - 记录培训过程中与销售助手的交互"""
    __tablename__ = "copilot_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("training_sessions.id"), nullable=False)

    # 消息类型: user_query/bot_response/suggestion
    message_type = Column(String(50), nullable=False)

    # 消息内容
    content = Column(Text, nullable=False)

    # 关联的轮次（如果是建议类型）
    round_number = Column(Integer, nullable=True)
    stage = Column(Integer, nullable=True)

    timestamp = Column(DateTime, default=datetime.utcnow)

    # 关系
    session = relationship("TrainingSession", backref="copilot_messages")

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "message_type": self.message_type,
            "content": self.content,
            "round_number": self.round_number,
            "stage": self.stage,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
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


# ==================== 数字面试官模型 ====================

class InterviewerProfileRegistry(Base):
    """面试官画像文件注册表 - 记录已导入的文件，避免重复导入"""
    __tablename__ = "interviewer_profile_registry"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), unique=True, nullable=False, index=True)
    file_hash = Column(String(64), nullable=False)
    interviewer_profile_id = Column(Integer, nullable=True)
    interviewer_name = Column(String(100), nullable=True)
    status = Column(String(20), default="success")
    imported_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "file_hash": self.file_hash,
            "interviewer_profile_id": self.interviewer_profile_id,
            "interviewer_name": self.interviewer_name,
            "status": self.status,
            "imported_at": self.imported_at.isoformat() if self.imported_at else None,
        }


class InterviewerProfile(Base):
    """面试官画像表 - 存储面试官的结构化信息"""
    __tablename__ = "interviewer_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    title = Column(String(100), nullable=True)
    company = Column(String(100), nullable=True)

    # 面试官特征
    expertise_areas = Column(Text, nullable=True)
    interview_style = Column(Text, nullable=True)
    personality_traits = Column(Text, nullable=True)
    question_preferences = Column(Text, nullable=True)

    # AI相关
    system_prompt = Column(Text, nullable=True)
    raw_content = Column(Text, nullable=True)
    source_file_path = Column(String(500), nullable=True)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "title": self.title,
            "company": self.company,
            "expertise_areas": self.expertise_areas,
            "interview_style": self.interview_style,
            "personality_traits": self.personality_traits,
            "question_preferences": self.question_preferences,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class InterviewSession(Base):
    """面试会话表 - 记录每次面试的完整过程"""
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), unique=True, nullable=False, index=True)

    # 关联信息
    candidate_id = Column(String(100), nullable=True)
    candidate_name = Column(String(100), nullable=True)
    interviewer_profile_id = Column(Integer, ForeignKey("interviewer_profiles.id"), nullable=False)
    digital_human_id = Column(Integer, ForeignKey("digital_humans.id"), nullable=True)  # 使用的虚拟人形象
    resume_id = Column(Integer, ForeignKey("candidate_resumes.id"), nullable=True)  # 关联的简历ID

    # 冗余字段
    interviewer_name = Column(String(100), nullable=True)
    interviewer_title = Column(String(100), nullable=True)

    # 面试配置
    interview_type = Column(String(50), nullable=False)  # technical/hr/behavioral
    difficulty_level = Column(String(20), nullable=True)  # easy/medium/hard
    max_rounds = Column(Integer, default=5)  # 最大面试轮数，默认5轮
    scoring_template_id = Column(Integer, ForeignKey("scoring_templates.id"), nullable=True)  # 评分模板ID

    # 会话状态
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
    interviewer_profile = relationship("InterviewerProfile")

    def get_progress_info(self):
        """获取面试进度信息"""
        from datetime import datetime

        progress = {
            "current_round": self.current_round,
            "max_rounds": self.max_rounds,
            "progress_percentage": int((self.current_round / self.max_rounds) * 100) if self.max_rounds > 0 else 0,
            "elapsed_seconds": 0,
            "status": self.status
        }

        # 计算已用时间
        if self.started_at:
            if self.completed_at:
                elapsed = (self.completed_at - self.started_at).total_seconds()
            else:
                elapsed = (datetime.utcnow() - self.started_at).total_seconds()
            progress["elapsed_seconds"] = int(elapsed)

        return progress

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "candidate_id": self.candidate_id,
            "candidate_name": self.candidate_name,
            "interviewer_profile_id": self.interviewer_profile_id,
            "interviewer_name": self.interviewer_name,
            "interviewer_title": self.interviewer_title,
            "resume_id": self.resume_id,
            "interview_type": self.interview_type,
            "difficulty_level": self.difficulty_level,
            "max_rounds": self.max_rounds,
            "scoring_template_id": self.scoring_template_id,
            "current_round": self.current_round,
            "total_rounds": self.total_rounds,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class InterviewRound(Base):
    """面试轮次表 - 记录每一轮问答"""
    __tablename__ = "interview_rounds"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"), nullable=False)

    round_number = Column(Integer, nullable=False)

    # 问答内容
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)

    # 问题元数据
    question_type = Column(String(50), nullable=True)
    is_followup = Column(Boolean, default=False)

    # 重录相关
    retry_count = Column(Integer, default=0)  # 重录次数
    retry_history = Column(JSON, nullable=True)  # 重录历史记录

    # 实时评估
    answer_quality = Column(String(50), nullable=True)
    evaluation_data = Column(JSON, nullable=True)

    timestamp = Column(DateTime, default=datetime.utcnow)

    # 关系
    session = relationship("InterviewSession", backref="rounds")

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "round_number": self.round_number,
            "question": self.question,
            "answer": self.answer,
            "question_type": self.question_type,
            "is_followup": self.is_followup,
            "answer_quality": self.answer_quality,
            "evaluation_data": self.evaluation_data,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


class InterviewEvaluation(Base):
    """面试评估表 - 存储综合评估结果"""
    __tablename__ = "interview_evaluations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"), unique=True, nullable=False)

    # 多维度评分（扩展到8个维度）
    technical_score = Column(Integer, nullable=True)  # 技术能力
    communication_score = Column(Integer, nullable=True)  # 沟通表达
    problem_solving_score = Column(Integer, nullable=True)  # 问题解决
    cultural_fit_score = Column(Integer, nullable=True)  # 文化匹配
    innovation_score = Column(Integer, nullable=True)  # 创新能力
    teamwork_score = Column(Integer, nullable=True)  # 团队协作
    stress_handling_score = Column(Integer, nullable=True)  # 压力应对
    learning_ability_score = Column(Integer, nullable=True)  # 学习能力

    # 总分和等级
    total_score = Column(Integer, nullable=True)
    performance_level = Column(String(20), nullable=True)

    # 详细分析
    strengths = Column(JSON, nullable=True)
    weaknesses = Column(JSON, nullable=True)
    suggestions = Column(JSON, nullable=True)

    # 报告内容
    detailed_report = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    session = relationship("InterviewSession", backref="evaluation", uselist=False)

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "technical_score": self.technical_score,
            "communication_score": self.communication_score,
            "problem_solving_score": self.problem_solving_score,
            "cultural_fit_score": self.cultural_fit_score,
            "innovation_score": self.innovation_score,
            "teamwork_score": self.teamwork_score,
            "stress_handling_score": self.stress_handling_score,
            "learning_ability_score": self.learning_ability_score,
            "total_score": self.total_score,
            "performance_level": self.performance_level,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "suggestions": self.suggestions,
            "detailed_report": self.detailed_report,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class DigitalHuman(Base):
    """虚拟人形象表 - 存储独立的虚拟人形象库"""
    __tablename__ = "digital_humans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, index=True)  # 形象名称（文件夹名）
    display_name = Column(String(100), nullable=False)  # 显示名称
    description = Column(String(500), nullable=True)   # 形象描述
    gender = Column(String(20), nullable=True)  # 性别：male/female/other
    style = Column(String(50), nullable=True)  # 风格：formal/casual/tech等

    # 视频路径
    video_idle = Column(String(500), nullable=True)    # 等待状态视频路径
    video_speaking = Column(String(500), nullable=True)  # 说话状态视频路径
    video_listening = Column(String(500), nullable=True)  # 倾听状态视频路径
    video_thinking = Column(String(500), nullable=True)  # 思考状态视频路径

    # 状态
    is_active = Column(Boolean, default=True)          # 是否启用
    is_default = Column(Boolean, default=False)        # 是否为默认形象

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "gender": self.gender,
            "style": self.style,
            "video_idle": self.video_idle,
            "video_speaking": self.video_speaking,
            "video_listening": self.video_listening,
            "video_thinking": self.video_thinking,
            "is_active": self.is_active,
            "is_default": self.is_default,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class InterviewExperienceSet(Base):
    """面经集 - 管理上传的面经文件"""
    __tablename__ = "interview_experience_set"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)           # 面经集名称
    description = Column(Text, nullable=True)            # 描述
    source_filename = Column(String(255), nullable=True) # 原始PDF文件名
    company = Column(String(100), nullable=True)         # 目标公司（可选）
    position = Column(String(100), nullable=True)        # 目标职位（可选）
    interview_type = Column(String(50), nullable=True)   # 面试类型
    question_count = Column(Integer, default=0)          # 问题数量
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # 关系
    questions = relationship("InterviewKnowledge", back_populates="experience_set", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "source_filename": self.source_filename,
            "company": self.company,
            "position": self.position,
            "interview_type": self.interview_type,
            "question_count": self.question_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_active": self.is_active,
        }


class InterviewKnowledge(Base):
    """面试知识库表 - 存储面试题库和评估标准"""
    __tablename__ = "interview_knowledge"

    id = Column(Integer, primary_key=True, autoincrement=True)
    interview_type = Column(String(50), nullable=False, index=True)
    category = Column(String(100), nullable=True)
    content = Column(Text, nullable=False)
    difficulty_level = Column(String(20), nullable=True)
    source_filename = Column(String(255), nullable=True)
    embedding = Column(LargeBinary, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 面经集关联字段
    experience_set_id = Column(Integer, ForeignKey('interview_experience_set.id'), nullable=True)
    question_text = Column(Text, nullable=True)          # 原始问题文本
    reference_answer = Column(Text, nullable=True)       # 参考答案（如果有）
    tags = Column(JSON, nullable=True)                   # 标签（如：高频、必考）

    # 关系
    experience_set = relationship("InterviewExperienceSet", back_populates="questions")

    def to_dict(self):
        return {
            "id": self.id,
            "interview_type": self.interview_type,
            "category": self.category,
            "content": self.content,
            "difficulty_level": self.difficulty_level,
            "source_filename": self.source_filename,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "experience_set_id": self.experience_set_id,
            "question_text": self.question_text,
            "reference_answer": self.reference_answer,
            "tags": self.tags,
        }


# ==================== 简历分析模型 ====================

class CandidateResume(Base):
    """候选人简历表 - 存储简历文件和基本信息"""
    __tablename__ = "candidate_resumes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(String(100), nullable=True, index=True)  # 候选人ID
    candidate_name = Column(String(100), nullable=True, index=True)  # 候选人姓名

    # 文件信息
    file_path = Column(String(500), nullable=False)  # 简历文件路径
    file_type = Column(String(20), nullable=False)  # 文件类型：pdf/word/image
    file_hash = Column(String(64), nullable=True)  # 文件哈希值，用于去重

    # 解析状态
    parse_status = Column(String(20), default="pending")  # pending/processing/completed/failed
    parsed_data = Column(JSON, nullable=True)  # 解析后的结构化数据

    # 质量评分
    quality_score = Column(Integer, nullable=True)  # 简历质量评分 0-100
    completeness_score = Column(Integer, nullable=True)  # 完整性评分
    professionalism_score = Column(Integer, nullable=True)  # 专业性评分

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    analysis = relationship("ResumeAnalysis", back_populates="resume", uselist=False, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "candidate_id": self.candidate_id,
            "candidate_name": self.candidate_name,
            "file_path": self.file_path,
            "file_type": self.file_type,
            "parse_status": self.parse_status,
            "parsed_data": self.parsed_data,
            "quality_score": self.quality_score,
            "completeness_score": self.completeness_score,
            "professionalism_score": self.professionalism_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ResumeAnalysis(Base):
    """简历分析结果表 - 存储简历的详细分析结果"""
    __tablename__ = "resume_analysis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    resume_id = Column(Integer, ForeignKey("candidate_resumes.id", ondelete="CASCADE"), unique=True, nullable=False)

    # 基本信息提取
    contact_info = Column(JSON, nullable=True)  # 联系方式：电话、邮箱、地址
    education = Column(JSON, nullable=True)  # 教育背景列表
    work_experience = Column(JSON, nullable=True)  # 工作经历列表
    project_experience = Column(JSON, nullable=True)  # 项目经历列表
    skills = Column(JSON, nullable=True)  # 技能列表
    certifications = Column(JSON, nullable=True)  # 证书列表

    # 统计信息
    total_work_years = Column(Float, nullable=True)  # 总工作年限
    education_level = Column(String(50), nullable=True)  # 最高学历
    major = Column(String(100), nullable=True)  # 专业

    # 标签化
    skill_tags = Column(JSON, nullable=True)  # 技能标签
    industry_tags = Column(JSON, nullable=True)  # 行业标签
    position_tags = Column(JSON, nullable=True)  # 职位标签

    # 质量评估
    quality_issues = Column(JSON, nullable=True)  # 质量问题列表
    improvement_suggestions = Column(JSON, nullable=True)  # 改进建议
    risk_flags = Column(JSON, nullable=True)  # 风险标记（时间断层、频繁跳槽等）

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    resume = relationship("CandidateResume", back_populates="analysis")

    def to_dict(self):
        return {
            "id": self.id,
            "resume_id": self.resume_id,
            "contact_info": self.contact_info,
            "education": self.education,
            "work_experience": self.work_experience,
            "project_experience": self.project_experience,
            "skills": self.skills,
            "certifications": self.certifications,
            "total_work_years": self.total_work_years,
            "education_level": self.education_level,
            "major": self.major,
            "skill_tags": self.skill_tags,
            "industry_tags": self.industry_tags,
            "position_tags": self.position_tags,
            "quality_issues": self.quality_issues,
            "improvement_suggestions": self.improvement_suggestions,
            "risk_flags": self.risk_flags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class JobPosition(Base):
    """职位信息表 - 存储招聘职位信息"""
    __tablename__ = "job_positions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False, index=True)  # 职位名称
    department = Column(String(100), nullable=True)  # 部门
    company = Column(String(100), nullable=True)  # 公司名称

    # 职位要求
    requirements = Column(Text, nullable=True)  # 职位要求描述
    skills_required = Column(JSON, nullable=True)  # 必需技能列表
    skills_preferred = Column(JSON, nullable=True)  # 优选技能列表
    education_required = Column(String(50), nullable=True)  # 学历要求
    experience_years_min = Column(Integer, nullable=True)  # 最低工作年限
    experience_years_max = Column(Integer, nullable=True)  # 最高工作年限

    # 职位信息
    job_type = Column(String(50), nullable=True)  # 职位类型：technical/hr/sales等
    industry = Column(String(100), nullable=True)  # 行业
    location = Column(String(100), nullable=True)  # 工作地点
    salary_range = Column(String(100), nullable=True)  # 薪资范围

    # 状态
    is_active = Column(Boolean, default=True)  # 是否在招

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "department": self.department,
            "company": self.company,
            "requirements": self.requirements,
            "skills_required": self.skills_required,
            "skills_preferred": self.skills_preferred,
            "education_required": self.education_required,
            "experience_years_min": self.experience_years_min,
            "experience_years_max": self.experience_years_max,
            "job_type": self.job_type,
            "industry": self.industry,
            "location": self.location,
            "salary_range": self.salary_range,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ResumeJobMatch(Base):
    """简历职位匹配表 - 存储简历与职位的匹配结果"""
    __tablename__ = "resume_job_matches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    resume_id = Column(Integer, ForeignKey("candidate_resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("job_positions.id", ondelete="CASCADE"), nullable=False, index=True)

    # 匹配度评分
    match_score = Column(Integer, nullable=False)  # 综合匹配度 0-100
    skill_match_score = Column(Integer, nullable=True)  # 技能匹配度
    experience_match_score = Column(Integer, nullable=True)  # 经验匹配度
    education_match_score = Column(Integer, nullable=True)  # 学历匹配度

    # 匹配详情
    matched_skills = Column(JSON, nullable=True)  # 匹配的技能列表
    missing_skills = Column(JSON, nullable=True)  # 缺失的技能列表
    match_details = Column(JSON, nullable=True)  # 详细匹配信息

    # 优先级
    priority = Column(String(20), nullable=True)  # 优先级：high/medium/low

    # 建议
    recommendations = Column(JSON, nullable=True)  # 匹配建议

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "resume_id": self.resume_id,
            "job_id": self.job_id,
            "match_score": self.match_score,
            "skill_match_score": self.skill_match_score,
            "experience_match_score": self.experience_match_score,
            "education_match_score": self.education_match_score,
            "matched_skills": self.matched_skills,
            "missing_skills": self.missing_skills,
            "match_details": self.match_details,
            "priority": self.priority,
            "recommendations": self.recommendations,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# ==================== 评分模板模型 ====================

class ScoringTemplate(Base):
    """评分模板表 - 存储不同岗位的评分权重配置"""
    __tablename__ = "scoring_templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    job_type = Column(String(50), nullable=True)

    # 8个维度的权重（总和应为100）
    technical_weight = Column(Integer, default=25)
    communication_weight = Column(Integer, default=15)
    problem_solving_weight = Column(Integer, default=20)
    cultural_fit_weight = Column(Integer, default=10)
    innovation_weight = Column(Integer, default=10)
    teamwork_weight = Column(Integer, default=10)
    stress_handling_weight = Column(Integer, default=5)
    learning_ability_weight = Column(Integer, default=5)

    # 状态
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "job_type": self.job_type,
            "weights": {
                "technical": self.technical_weight,
                "communication": self.communication_weight,
                "problem_solving": self.problem_solving_weight,
                "cultural_fit": self.cultural_fit_weight,
                "innovation": self.innovation_weight,
                "teamwork": self.teamwork_weight,
                "stress_handling": self.stress_handling_weight,
                "learning_ability": self.learning_ability_weight
            },
            "is_active": self.is_active,
            "is_default": self.is_default,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# ==================== 面试模板模型 ====================

class InterviewTemplate(Base):
    """面试模板表 - 存储不同岗位的面试模板配置"""
    __tablename__ = "interview_templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    job_type = Column(String(50), nullable=True)

    # 面试配置
    max_rounds = Column(Integer, default=5)
    difficulty_level = Column(String(20), default="medium")

    # 关联的面经集（JSON数组存储ID列表）
    experience_set_ids = Column(JSON, nullable=True)

    # 关联的评分模板
    scoring_template_id = Column(Integer, ForeignKey("scoring_templates.id"), nullable=True)

    # 状态
    is_active = Column(Boolean, default=True)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'job_type': self.job_type,
            'max_rounds': self.max_rounds,
            'difficulty_level': self.difficulty_level,
            'experience_set_ids': self.experience_set_ids,
            'scoring_template_id': self.scoring_template_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


# ==================== 候选人管理模型 ====================

class Candidate(Base):
    """候选人信息表 - 存储候选人基本信息"""
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    email = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True)
    position = Column(String(100), nullable=True)
    status = Column(String(20), default="active")
    source = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "candidate_id": self.candidate_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "position": self.position,
            "status": self.status,
            "source": self.source,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
