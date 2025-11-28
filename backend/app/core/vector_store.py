"""
Vector store bridge for pgvector + FAISS
"""

from typing import List

from ..db import supabase


class PgVectorStore:
    """
    Vector search using Supabase pgvector
    """

    def similarity_search(self, query_embedding: List[float], k: int = 5):
        # Call the match_embeddings function via RPC
        response = supabase.rpc(
            "match_embeddings", {"query_embedding": query_embedding, "match_count": k}
        ).execute()

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
                "document_source": row.get("document_source"),
                "similarity": row.get("similarity"),
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
