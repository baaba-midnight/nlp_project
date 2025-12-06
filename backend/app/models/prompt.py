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
    has_chunks: Optional[bool]
