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
        # Supabase RPC call
        response = supabase.rpc(
            "match_embeddings",
            {
                "query_embedding": query_embedding,
                "match_count": k
            }
        ).execute()

        if not response.data:
            return []

        # return the actual chunks + metadata
        return response.data


class FaissVectorStore:
    """
    Fallback FAISS vector store
    """

    def __init__(self, faiss_store):
        self.faiss = faiss_store

    def similarity_search(self, query_embedding: List[float], k: int = 5):
        return self.faiss.similarity_search_by_vector(query_embedding, k)
