"""
Retriever module for RAG pipeline
"""
from sentence_transformers import SentenceTransformer
from .vector_store import PgVectorStore
from sentence_transformers import SentenceTransformer
   
class DenseRetriever:
    """
    Dense passage retrieval using bi-encoder architecture (Section 14.2)
    Encodes queries and documents separately using BERT-based models.
    """
    
    def __init__(self, embedder_model, similarity_threshold):
        """
        Initialize dense retriever with embedding model and vector store.
        Args:
            embedder_model: Model name for sentence embeddings
            similarity_threshold: Minimum similarity for passage relevance
        """
        self.embedder = SentenceTransformer(embedder_model)
        self.store = PgVectorStore()
        self.similarity_threshold = similarity_threshold
    
    def retrieve(self, query, k):
        """
        Retrieve top-k relevant passages using dense retrieval.
        Returns passages ranked by cosine similarity in embedding space.
        Args:
            query: User's question
            k: Number of passages to retrieve   
        Returns:
            List of retrieved passages with metadata
        """
        if not query or not query.strip():
            print("Empty query provided to retriever.")
            return []
        # Generate dense query embedding
        query_vec = self.embedder.encode(query, convert_to_tensor=False, normalize_embeddings=True).tolist()
        # Search vector store using dot product 
        results = self.store.similarity_search(query_vec, k, self.similarity_threshold)
        return results
          

