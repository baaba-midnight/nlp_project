"""
File: prompt.py
Project: models
File Created: Friday, 28th November 2025 1:15:59 PM
Author: baaba-midnight
Email: baaba.amosah@gmail.com
Version: 1.0
Brief: <<brief>>
-----
Last Modified: Friday, 28th November 2025 1:31:04 PM
Modified By: baaba-midnight
-----
Copyright ©2025 baaba-midnight
"""

from typing import Dict, List, Optional

from pydantic import BaseModel


class PromptCreate(BaseModel):
    query: str


class SourceItem(BaseModel):
    chunk: str
    similarity: Optional[float] = None
    metadata: Optional[Dict] = None


class PromptOut(BaseModel):
    answer: str
    sources: List[SourceItem]
    error: Optional[str]
