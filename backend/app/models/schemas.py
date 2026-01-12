from pydantic import BaseModel
from typing import List, Optional

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
