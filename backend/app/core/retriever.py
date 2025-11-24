"""
Retriever module for RAG pipeline
"""
from sentence_transformers import SentenceTransformer
from app.core.vector_store import PgVectorStore, FaissVectorStore



class Retriever:
    def __init__(self, use_faiss=False, faiss_store=None):
        self.use_faiss = use_faiss
        self.embedder = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

        if use_faiss:
            self.store = FaissVectorStore(faiss_store)
        else:
            self.store = PgVectorStore()

    def retrieve(self, query: str, k: int = 5):
        query_vec = self.embedder.encode(query).tolist()
        results = self.store.similarity_search(query_vec, k)
        return results