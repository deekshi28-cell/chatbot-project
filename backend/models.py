from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ChatMessage(BaseModel):
    message: str
    session_id: str
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: datetime

class MessageDocument(BaseModel):
    session_id: str
    message: str
    sender: str  # "user" or "bot"
    timestamp: datetime
    user_id: Optional[str] = None
