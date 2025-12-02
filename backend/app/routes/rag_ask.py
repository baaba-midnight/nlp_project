"""
File: rag_ask.py
Project: routes
File Created: Wednesday, 26th November 2025 12:21:33 PM
Author: baaba-midnight
Email: baaba.amosah@gmail.com
Version: 1.0
Brief: <<brief>>
-----
Last Modified: Tuesday, 2nd December 2025 1:07:46 PM
Modified By: baaba-midnight
-----
Copyright ©2025 baaba-midnight
"""

from ..core.rag_pipeline import RAGPipeline
from ..models.prompt import PromptCreate, PromptOut

pipeline = RAGPipeline(
    similarity_threshold=0.4,
    embedder_model="sentence-transformers/all-MiniLM-L6-v2",
    language_model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
)


def rag_ask(payload: PromptCreate) -> PromptOut:
    """Run RAG pipeline for the given prompt and return a PromptOut object.

    This is a plain function (not an HTTP route) so it can be called from Streamlit.
    """
    query = payload.query
    output = pipeline.run(query=query, k=10, max_input_length=2048, max_new_tokens=1500)

    # Normalize sources into SourceItem-compatible dicts (chunk, similarity, metadata)
    sources = []
    for s in output.get("sources", []) or []:
        if isinstance(s, dict):
            sources.append({
                "chunk": s.get("chunk") if s.get("chunk") is not None else str(s),
                "similarity": float(s.get("similarity"))
                if s.get("similarity") is not None
                else None,
                "metadata": s.get("metadata")
                if s.get("metadata") is not None
                else None,
            })
        else:
            # fallback: coerce to string
            sources.append({"chunk": str(s), "similarity": None, "metadata": None})

    return PromptOut(
        answer=output.get("answer", ""),
        sources=sources,
        confidence=output.get("confidence"),
        error=output.get("error"),
    )
