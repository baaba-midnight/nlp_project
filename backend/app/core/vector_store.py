"""
Vector store bridge for pgvector
"""

from ..db import supabase


class PgVectorStore:
    """
    Vector store using Supabase pgvector for dense passage retrieval.
    Stores document embeddings and performs similarity search.
    """
    
    def __init__(self):
        self.supabase = supabase

    def similarity_search(self, query_embedding, k, similarity_threshold):
        """
        Search using cosine similarity in embedding space.
        Args:
            query_embedding: Embedding vector of the query
            k: Number of top similar passages to retrieve
            similarity_threshold: Minimum similarity score to consider relevant
        Returns:
            List of dicts with chunk, metadata, similarity, and document info
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
            # Apply similarity threshold
            if similarity < similarity_threshold:
                continue
                
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
