from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.app.core.rag_pipeline import RAGPipeline
from backend.app.services.ingestor import Document as AppDocument

router = APIRouter()
rag_pipeline = RAGPipeline(use_faiss=True)  # or False for Supabase

class QueryRequest(BaseModel):
    query: str

@router.post("/rag/ask")
async def ask_question(req: QueryRequest):
    try:
        result = rag_pipeline.ask(req.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/embed/upload")
async def upload_document(doc: AppDocument):
    try:
        result = rag_pipeline.ingest_document(doc)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
