"""
File: rag_ask.py
Project: routes
File Created: Wednesday, 26th November 2025 12:21:33 PM
Author: baaba-midnight
Email: baaba.amosah@gmail.com
Version: 1.0
Brief: <<brief>>
-----
Last Modified: Friday, 28th November 2025 2:52:01 PM
Modified By: baaba-midnight
-----
Copyright ©2025 baaba-midnight
"""
from fastapi import APIRouter
from ..core.rag_pipeline import RAGPipeline
from ..models.prompt import PromptCreate, PromptOut

router = APIRouter()

pipeline = RAGPipeline(use_faiss=False, similarity_threshold = 0.4)

@router.post("/rag/ask")
def rag_ask(payload: PromptCreate) -> PromptOut:
    query = payload.query
    output = pipeline.run(query, k = 10)
    # Normalize sources into SourceItem-compatible dicts (chunk, similarity, metadata)
    sources = []
    for s in output.get("sources", []) or []:
        if isinstance(s, dict):
            sources.append({
                "chunk": s.get("chunk") if s.get("chunk") is not None else str(s),
                "similarity": float(s.get("similarity")) if s.get("similarity") is not None else None,
                "metadata": s.get("metadata") if s.get("metadata") is not None else None,
            })
        else:
            # fallback: coerce to string
            sources.append({"chunk": str(s), "similarity": None, "metadata": None})

    return PromptOut(
        answer=output.get("answer", ""),
        sources=sources,
        error=output.get("error"),
    )