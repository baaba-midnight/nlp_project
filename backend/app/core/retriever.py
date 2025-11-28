"""
Retriever module for RAG pipeline
"""
from sentence_transformers import SentenceTransformer
from app.core.vector_store import PgVectorStore, FaissVectorStore
from sentence_transformers import SentenceTransformer
from typing import Dict, List


   
class DenseRetriever:
    """
    Dense passage retrieval using bi-encoder architecture (Section 14.2)
    Encodes queries and documents separately using BERT-based models.
    
    Uses the architecture from Eq. 14.18:
    z_q = BERT_Q(q)[CLS]
    z_d = BERT_D(d)[CLS]
    score(q, d) = z_q · z_d
    """
    
    def __init__(self, use_faiss=False, faiss_store=None, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.use_faiss = use_faiss
        self.embedder = SentenceTransformer(model_name)
        
        # Initialize vector store
        if use_faiss:
            self.store = FaissVectorStore(faiss_store)            
        else:
            self.store = PgVectorStore()
    
    def retrieve(self, query: str, k: int = 5) -> List[Dict]:
        """
        Retrieve top-k relevant passages using dense retrieval.
        Returns passages ranked by cosine similarity in embedding space.
        """
        if not query or not query.strip():
            print("Empty query provided to retriever.")
            return []
        # Generate dense query embedding
        query_vec = self.embedder.encode(query, convert_to_tensor=False, normalize_embeddings=True).tolist()
        # Search vector store using dot product (equivalent to cosine for normalized vectors)
        results = self.store.similarity_search(query_vec, k)
        print(f"Retrieved {len(results)} results for query: {query[:50]}...")
        return results
          

