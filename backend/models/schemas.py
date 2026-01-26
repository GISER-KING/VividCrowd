from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AgentProfile(BaseModel):
    name: str
    age: int
    gender: str
    occupation: str
    personality_traits: List[str]
    interests: List[str]
    speech_style: str
    avoid_topics: List[str]
    guardrail_rules: List[str]
    system_prompt: str

class ChatMessage(BaseModel):
    sender: str
    content: str
    is_user: bool = False
    timestamp: float = 0.0

class WebSocketMessage(BaseModel):
    type: str  # 'text', 'stream_start', 'stream_chunk', 'stream_end', 'error'
    sender: str
    content: str


# ========== 名人数字分身相关模型 ==========

class CelebrityBase(BaseModel):
    name: str
    source_type: str = "person"  # person/book/topic
    author: Optional[str] = None
    birth_year: Optional[int] = None
    death_year: Optional[int] = None
    nationality: Optional[str] = None
    occupation: Optional[str] = None
    biography: Optional[str] = None
    famous_works: Optional[str] = None
    famous_quotes: Optional[str] = None
    personality_traits: Optional[str] = None
    speech_style: Optional[str] = None

class CelebrityCreate(CelebrityBase):
    system_prompt: Optional[str] = None
    raw_content: Optional[str] = None
    source_pdf_path: Optional[str] = None

class CelebrityResponse(CelebrityBase):
    id: int
    system_prompt: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CelebrityChatMessage(BaseModel):
    message: str
    celebrity_ids: List[int]
    mode: str = "private"  # private/group


# ========== 数字客户相关模型 ==========

class CustomerProfileBase(BaseModel):
    name: str
    age_range: Optional[str] = None
    gender: Optional[str] = None
    occupation: Optional[str] = None
    industry: Optional[str] = None
    personality_traits: Optional[str] = None
    communication_style: Optional[str] = None
    pain_points: Optional[str] = None
    needs: Optional[str] = None
    objections: Optional[str] = None

class CustomerProfileCreate(CustomerProfileBase):
    system_prompt: Optional[str] = None
    raw_content: Optional[str] = None
    source_file_path: Optional[str] = None

class CustomerProfileResponse(CustomerProfileBase):
    id: int
    system_prompt: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CustomerChatMessage(BaseModel):
    message: str
    customer_ids: List[int]
    mode: str = "private"  # private/group
