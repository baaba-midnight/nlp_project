from fastapi import APIRouter
from app.core.rag_pipeline import RAGPipeline

router = APIRouter()

pipeline = RAGPipeline(use_faiss=False)

@router.post("/rag/ask")
def rag_ask(payload: dict):
    query = payload.get("query", "")
    output = pipeline.run(query)
    return output