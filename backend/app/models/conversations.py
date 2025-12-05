from typing import Optional

from pydantic import BaseModel


class MessageCreate(BaseModel):
    prompt: str


class MessageOut(BaseModel):
    id: str
    prompt: str
    answer: str
    context_chunks: Optional[list]
    created_at: str


class ConversationOut(BaseModel):
    id: str
    title: str
    created_at: str
    last_active_at: str
