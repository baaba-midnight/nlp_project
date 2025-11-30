"""
Vector store bridge for pgvector + FAISS
"""
from typing import List, Dict
from ..db import supabase


class PgVectorStore:
    """
    Vector store using Supabase pgvector for dense passage retrieval.
    Stores document embeddings and performs similarity search.
    """
    
    def __init__(self):
        self.supabase = supabase

    def similarity_search(self, query_embedding: List[float], k: int = 5) -> List[Dict]:
        """
        Search using cosine similarity in embedding space.
        Implements dense retrieval as described in Section 14.2.
        """
        if not query_embedding:
            print("Empty query embedding provided to vector store.")
            return []
            
        if k <= 0:
            print("Invalid value of k provided to vector store.")
            return []
            
        # Call RPC function for vector similarity search
        response = self.supabase.rpc(
            "match_embeddings",
                {
                    "query_embedding": query_embedding,
                    "match_count": k
                }
            ).execute()
            
        if not response.data:
            print("No results returned from vector store.")
            return []
            
        # Parse and validate results
        results = []
        for row in response.data:
            # Ensure similarity is float
            similarity = row.get("similarity", 0.0)
            similarity = float(similarity)
                
            results.append({
                "chunk": row.get("chunk", ""),
                "chunk_index": row.get("chunk_index"),
                "metadata": row.get("metadata", {}),
                "document_id": row.get("document_id"),
                "document_title": row.get("document_title", "Unknown"),
                "document_source": row.get("document_source", "Unknown"),
                "similarity": similarity
            })
        return results


class FaissVectorStore:
    """Fallback FAISS vector store for approximate nearest neighbor search"""
    
    def __init__(self, faiss_store):
        self.faiss = faiss_store
        
    def similarity_search(self, query_embedding: List[float], k: int = 5) -> List[Dict]:
        """Approximate nearest neighbor search using FAISS (Section 14.2)"""
        return self.faiss_similarity_search_by_vector(query_embedding, k)