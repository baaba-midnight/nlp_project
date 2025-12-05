from pydantic import BaseModel
from typing import Optional


class MessageCreate(BaseModel):
    role: str
    content: str
    metadata: Optional[dict] = None
    tokens: Optional[int] = None


class ConversationOut(BaseModel):
    id: str
    title: Optional[str]
    language: Optional[str]
    context_metadata: Optional[dict]
    active: Optional[bool]
    created_at: Optional[str]
    last_active_at: Optional[str]
