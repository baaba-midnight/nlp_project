"""
File: conversations.py
Project: models
File Created: Thursday, 27th November 2025 7:13:12 PM
Author: baaba-midnight
Email: baaba.amosah@gmail.com
Version: 1.0
Brief: <<brief>>
-----
Last Modified: Thursday, 27th November 2025 7:15:08 PM
Modified By: baaba-midnight
-----
Copyright ©2025 baaba-midnight
"""

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
