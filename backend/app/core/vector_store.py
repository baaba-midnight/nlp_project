"""
Vector store bridge for pgvector + FAISS
"""
from typing import List
import numpy as np
from app.db import supabase


class PgVectorStore:
    """
    Vector search using Supabase pgvector 
    """

    def similarity_search(self, query_embedding: List[float], k: int = 5):
        # Direct SQL query using pgvector <=> operator for similarity
        sql = """
            SELECT e.id, e.document_id, e.chunk_index, e.chunk, e.metadata,
                   d.title AS document_title, d.source AS document_source
            FROM embeddings e
            JOIN documents d ON d.id = e.document_id
            ORDER BY e.embedding <=> $1
            LIMIT $2
        """
        response = supabase.rpc("sql", {"query": sql, "params": [query_embedding, k]}).execute()

        if not response.data:
            return []

        results = []
        for row in response.data:
            results.append({
                "chunk": row.get("chunk"),
                "chunk_index": row.get("chunk_index"),
                "metadata": row.get("metadata"),
                "document_id": row.get("document_id"),
                "document_title": row.get("document_title"),
                "document_source": row.get("document_source")
            })

        return results

class FaissVectorStore:
    """
    Fallback FAISS vector store
    """

    def __init__(self, faiss_store):
        self.faiss = faiss_store

    def similarity_search(self, query_embedding: List[float], k: int = 5):
        return self.faiss.similarity_search_by_vector(query_embedding, k)
