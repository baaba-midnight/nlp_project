"""
File: rag_ask.py
Project: routes
File Created: Wednesday, 26th November 2025 12:21:33 PM
Author: baaba-midnight
Email: baaba.amosah@gmail.com
Version: 1.0
Brief: <<brief>>
-----
Last Modified: Saturday, 6th December 2025 8:15:32 PM
Modified By: baaba-midnight
-----
Copyright ©2025 baaba-midnight
"""

from fastapi import APIRouter

from ..core.rag_pipeline import RAGPipeline
from ..models.prompt import PromptCreate, PromptOut
import os
from dotenv import load_dotenv

load_dotenv()

# Get colab_url from environment, default to None
colab_url = os.getenv("colab_url")
print(f"colab_url from env: {colab_url}")   
use_colab_api = colab_url is not None and colab_url.strip() != ""

# If colab_url is not set, use local model instead
if not use_colab_api:
    print("No colab_url found in environment. Using local model instead.")
    print("To use Colab API, set colab_url in your .env file")

pipeline = RAGPipeline(
    similarity_threshold=0.4,
    embedder_model="sentence-transformers/all-MiniLM-L6-v2",
    language_model="alotanna/llama2-7b-ghana-climate",
    use_colab_api=use_colab_api,
    colab_url=colab_url
)

router = APIRouter(prefix="/rag", tags=["rag"])

@router.post("/ask")
def rag_ask(payload: PromptCreate) -> PromptOut:
    """Run RAG pipeline for the given prompt and return a PromptOut object.

    This is a plain function (not an HTTP route) so it can be called from Streamlit.
    """
    query = payload.query
    output = pipeline.run(query=query, k=10)

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
        has_chunks=output.get("has_chunks")
    )
