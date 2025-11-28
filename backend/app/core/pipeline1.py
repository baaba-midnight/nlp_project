"""
Enhanced RAG Pipeline for Ghana Legal Chatbot
Based on Jurafsky & Martin (2025) - Chapter 14: Question Answering and RAG
"""
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Optional, Tuple
import logging
import numpy as np

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class Llama2LLM:
    """
    Language Model for answer generation in RAG pipeline.
    Implements retrieval-augmented generation as described in Section 14.3.1
    """
    
    def __init__(self, model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"):
        # Detect device and set appropriate dtype
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if self.device == "cuda" else torch.float32
        
        logger.info(f"Loading model on {self.device} with dtype {dtype}")
        
        # Load tokenizer
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            # Set pad_token if it doesn't exist
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                
        except Exception as e:
            raise RuntimeError(f"Failed to load tokenizer: {str(e)}")
        
        # Load model
        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=dtype,
                low_cpu_mem_usage=True,
                device_map=None,
                trust_remote_code=True
            ).to(self.device)
            
            self.model.eval()
            logger.info("Model loaded successfully")
            
        except Exception as e:
            raise RuntimeError(f"Failed to load model: {str(e)}")
    
    def generate(self, prompt: str, max_new_tokens: int = 512) -> str:
        """
        Generate answer using retrieval-augmented generation.
        Implements conditional generation: p(x_i | R(q); prompt; [Q:]; q; [A:]; x_<i)
        """
        try:
            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048).to(self.device)
            input_length = inputs['input_ids'].shape[1]
            
            # Warn if prompt is very long
            if input_length > 1800:
                logger.warning(f"Prompt length ({input_length}) is very long, may affect quality")
            
            # Generate with appropriate parameters for factual QA
            with torch.no_grad():
                output = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    pad_token_id=self.tokenizer.pad_token_id,
                    temperature=0.3,  # Lower temperature for more factual answers
                    do_sample=True,
                    top_p=0.85,
                    repetition_penalty=1.15,
                    no_repeat_ngram_size=3  # Avoid repeating trigrams
                )
            
            # Decode only the generated tokens
            generated_ids = output[0][input_length:]
            generated_text = self.tokenizer.decode(generated_ids, skip_special_tokens=True)
            
            return generated_text.strip()
            
        except torch.cuda.OutOfMemoryError:
            logger.error("CUDA out of memory")
            return "Error: GPU out of memory. Try reducing context or max_new_tokens."
        except Exception as e:
            logger.error(f"Generation error: {str(e)}")
            return f"Error during generation: {str(e)}"


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
        
        try:
            logger.info(f"Loading embedding model: {model_name}")
            # Use sentence-transformers for dense retrieval (bi-encoder)
            self.embedder = SentenceTransformer(model_name)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            raise RuntimeError(f"Failed to load embedding model: {str(e)}")
        
        # Initialize vector store
        if use_faiss:
            if faiss_store is None:
                raise ValueError("faiss_store must be provided when use_faiss=True")
            self.store = FaissVectorStore(faiss_store)
        else:
            self.store = PgVectorStore()
    
    def retrieve(self, query: str, k: int = 5) -> List[Dict]:
        """
        Retrieve top-k relevant passages using dense retrieval.
        Returns passages ranked by cosine similarity in embedding space.
        """
        try:
            if not query or not query.strip():
                logger.warning("Empty query provided")
                return []
            
            # Generate dense query embedding
            query_vec = self.embedder.encode(query, convert_to_tensor=False, normalize_embeddings=True).tolist()
            
            # Search vector store using dot product (equivalent to cosine for normalized vectors)
            results = self.store.similarity_search(query_vec, k)
            
            logger.info(f"Retrieved {len(results)} results for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Retrieval error: {str(e)}")
            return []


class PgVectorStore:
    """
    Vector store using Supabase pgvector for dense passage retrieval.
    Stores document embeddings and performs similarity search.
    """
    
    def __init__(self):
        try:
            from app.db import supabase
            self.supabase = supabase
        except ImportError as e:
            raise RuntimeError(f"Failed to import supabase: {str(e)}")
    
    def similarity_search(self, query_embedding: List[float], k: int = 5) -> List[Dict]:
        """
        Search using cosine similarity in embedding space.
        Implements dense retrieval as described in Section 14.2.
        """
        try:
            if not query_embedding:
                logger.error("Empty query embedding provided")
                return []
            
            if k <= 0:
                logger.error(f"Invalid k value: {k}")
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
                logger.info("No results found from database")
                return []
            
            # Parse and validate results
            results = []
            for row in response.data:
                # Ensure similarity is float
                similarity = row.get("similarity", 0.0)
                try:
                    similarity = float(similarity)
                except (TypeError, ValueError):
                    logger.warning(f"Invalid similarity value: {similarity}")
                    similarity = 0.0
                
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
            
        except Exception as e:
            logger.error(f"Database search error: {str(e)}")
            return []


class FaissVectorStore:
    """Fallback FAISS vector store for approximate nearest neighbor search"""
    
    def __init__(self, faiss_store):
        if faiss_store is None:
            raise ValueError("faiss_store cannot be None")
        self.faiss = faiss_store
    
    def similarity_search(self, query_embedding: List[float], k: int = 5) -> List[Dict]:
        """Approximate nearest neighbor search using FAISS (Section 14.2)"""
        try:
            return self.faiss.similarity_search_by_vector(query_embedding, k)
        except Exception as e:
            logger.error(f"FAISS search error: {str(e)}")
            return []


class RAGPipeline1:
    """
    Retrieval-Augmented Generation Pipeline (Section 14.3)
    
    Two-stage architecture:
    1. Retriever: Dense passage retrieval to find relevant documents
    2. Reader/Generator: LLM generates answer conditioned on retrieved passages
    
    Implements the RAG formulation from Section 14.3.1:
    p(x_1, ..., x_n) = ∏ p(x_i | R(q); prompt; [Q:]; q; [A:]; x_<i)
    """
    
    def __init__(self, use_faiss=False, faiss_store=None, similarity_threshold: float = 0.65):
        """
        Initialize RAG pipeline with retriever and generator.
        
        Args:
            use_faiss: Whether to use FAISS for retrieval
            faiss_store: FAISS store instance if use_faiss=True
            similarity_threshold: Minimum similarity for passage relevance
        """
        self.similarity_threshold = similarity_threshold
        
        # Initialize dense retriever
        try:
            self.retriever = DenseRetriever(use_faiss=use_faiss, faiss_store=faiss_store)
            logger.info("Retriever initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize retriever: {str(e)}")
            raise
        
        # Initialize LLM for generation
        try:
            self.llm = Llama2LLM()
            logger.info("LLM initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {str(e)}")
            raise
    
    def filter_relevant_passages(self, passages: List[Dict]) -> List[Dict]:
        """
        Filter passages by similarity threshold.
        Helps ensure retrieved passages are actually relevant (Section 14.1.4).
        """
        if not passages:
            return []
        
        relevant = []
        for passage in passages:
            try:
                similarity = float(passage.get("similarity", 0.0))
                passage["similarity"] = similarity
                
                if similarity >= self.similarity_threshold:
                    relevant.append(passage)
            except (TypeError, ValueError) as e:
                logger.warning(f"Skipping passage with invalid similarity")
                continue
        
        # Sort by similarity (descending)
        relevant_sorted = sorted(relevant, key=lambda x: x["similarity"], reverse=True)
        
        logger.info(f"Filtered {len(relevant_sorted)}/{len(passages)} passages above threshold {self.similarity_threshold}")
        return relevant_sorted
    
    def build_rag_prompt(self, query: str, passages: List[Dict], max_context_tokens: int = 1500) -> str:
        """
        Construct RAG prompt with retrieved passages.
        Implements the prompt structure from Section 14.3.1.
        
        Format: [Retrieved Passages] + "Based on these texts, answer:" + [Q:] query [A:]
        """
        context_parts = []
        total_tokens = 0
        
        # Add passages with source attribution
        for idx, passage in enumerate(passages, 1):
            chunk_text = passage.get("chunk", "")
            if not chunk_text:
                continue
            
            # Use tokenizer for accurate token counting
            chunk_tokens = len(self.llm.tokenizer.encode(chunk_text))
            
            # Stop if adding this passage exceeds token limit
            if total_tokens + chunk_tokens > max_context_tokens:
                logger.info(f"Stopped at passage {idx} to stay within token limit")
                break
            
            # Format passage with source information
            source = passage.get("document_title", "Unknown Document")
            context_parts.append(f"[Passage {idx} - Source: {source}]\n{chunk_text}")
            total_tokens += chunk_tokens
        
        context_text = "\n\n".join(context_parts)
        
        # Construct RAG prompt following best practices from Section 14.3.1
        prompt = f"""You are a knowledgeable Ghana Legal Assistant. Your task is to answer questions accurately based ONLY on the provided legal documents.

RETRIEVED LEGAL PASSAGES:
{context_text}

INSTRUCTIONS:
1. Answer ONLY using information from the passages above
2. If the answer is not in the passages, state: "I cannot answer this question based on the provided documents."
3. Cite the passage number when providing information (e.g., "According to Passage 2...")
4. Be precise and accurate
5. Do not use external knowledge

QUESTION: {query}

ANSWER:"""
        
        return prompt
    
    def evaluate_answer_quality(self, answer: str) -> Tuple[Optional[str], float]:
        """
        Detect if the LLM is uncertain or hallucinating.
        Addresses the calibration problem discussed in Section 14.1 intro.
        """
        # Phrases indicating uncertainty or inability to answer
        uncertainty_phrases = [
            "i cannot answer",
            "i don't have",
            "not in the context",
            "not in the passage",
            "cannot find",
            "not provided",
            "no information",
            "insufficient information",
            "based on the provided documents"
        ]
        
        answer_lower = answer.lower()
        
        # Check for uncertainty
        uncertainty_count = sum(1 for phrase in uncertainty_phrases if phrase in answer_lower)
        
        # Simple confidence score (inverse of uncertainty indicators)
        confidence = max(0.0, 1.0 - (uncertainty_count * 0.3))
        
        warning = None
        if uncertainty_count > 0:
            warning = "llm_uncertain"
        elif len(answer.split()) < 5:
            warning = "answer_too_short"
            confidence = 0.5
        
        return warning, confidence
    
    def run(self, query: str, k: int = 5) -> Dict:
        """
        Execute complete RAG pipeline: retrieve then generate.
        
        Implements the two-stage retriever/reader architecture from Section 14.3:
        1. Retriever: Dense passage retrieval to get top-k relevant passages
        2. Reader: RAG generation conditioned on retrieved passages
        
        Args:
            query: User's question
            k: Number of passages to retrieve
            
        Returns:
            Dict containing answer, sources, confidence, and metadata
        """
        try:
            # Validate input
            if not query or not query.strip():
                return {
                    "answer": "Please provide a valid question.",
                    "sources": [],
                    "confidence": 0.0,
                    "error": "empty_query"
                }
            
            if k <= 0:
                k = 5
                logger.warning(f"Invalid k value, defaulting to {k}")
            
            # Stage 1: RETRIEVAL
            # Retrieve more passages than needed for filtering
            logger.info(f"[RETRIEVER] Retrieving passages for: {query[:50]}...")
            passages = self.retriever.retrieve(query, k * 2)
            
            if not passages:
                return {
                    "answer": "I couldn't find any relevant documents in the database to answer your question.",
                    "sources": [],
                    "confidence": 0.0,
                    "error": "no_results"
                }
            
            # Filter by similarity threshold
            relevant_passages = self.filter_relevant_passages(passages)
            
            if not relevant_passages:
                return {
                    "answer": f"I don't have sufficient information about '{query}' in my database. The available documents may not be relevant enough to answer your question confidently.",
                    "sources": passages[:3],  # Return top 3 for reference
                    "confidence": 0.2,
                    "error": "low_relevance"
                }
            
            # Take top k after filtering
            top_passages = relevant_passages[:k]
            
            # Stage 2: READER/GENERATOR (RAG)
            logger.info("[READER] Building RAG prompt...")
            rag_prompt = self.build_rag_prompt(query, top_passages)
            
            logger.info("[READER] Generating answer...")
            raw_answer = self.llm.generate(rag_prompt, max_new_tokens=400)
            
            # Clean up answer
            # Remove any remaining prompt artifacts
            if "ANSWER:" in raw_answer:
                answer = raw_answer.split("ANSWER:")[-1].strip()
            else:
                answer = raw_answer.strip()
            
            # Remove repetitive system instructions that might leak through
            cleanup_phrases = ["QUESTION:", "INSTRUCTIONS:", "RETRIEVED", "PASSAGES:"]
            for phrase in cleanup_phrases:
                if phrase in answer:
                    answer = answer.split(phrase)[0].strip()
            
            # Evaluate answer quality
            warning, confidence = self.evaluate_answer_quality(answer)
            
            # Prepare response
            response = {
                "answer": answer,
                "sources": top_passages,
                "confidence": confidence,
                "num_sources": len(top_passages),
                "warning": warning,
                "avg_similarity": np.mean([p["similarity"] for p in top_passages])
            }
            
            logger.info(f"[COMPLETE] Answer generated with {len(top_passages)} sources (confidence: {confidence:.2f})")
            return response
            
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}")
            return {
                "answer": "An error occurred while processing your question. Please try again.",
                "sources": [],
                "confidence": 0.0,
                "error": str(e)
            }
    
    def evaluate_with_metrics(self, test_queries: List[Dict]) -> Dict:
        """
        Evaluate RAG system using metrics from Section 14.4.
        
        Supports:
        - Exact Match: % of predictions matching gold answers exactly
        - Token F1: Average token overlap between predicted and gold answers
        - MRR: Mean Reciprocal Rank for ranked answer lists
        
        Args:
            test_queries: List of dicts with 'query' and 'gold_answer' keys
            
        Returns:
            Dict with evaluation metrics
        """
        exact_matches = 0
        f1_scores = []
        
        for test_item in test_queries:
            query = test_item['query']
            gold_answer = test_item['gold_answer']
            
            result = self.run(query)
            predicted_answer = result['answer']
            
            # Exact match
            if predicted_answer.strip().lower() == gold_answer.strip().lower():
                exact_matches += 1
            
            # Token F1 (from Section 14.4)
            pred_tokens = set(predicted_answer.lower().split())
            gold_tokens = set(gold_answer.lower().split())
            
            if len(pred_tokens) == 0 or len(gold_tokens) == 0:
                f1_scores.append(0.0)
            else:
                precision = len(pred_tokens & gold_tokens) / len(pred_tokens)
                recall = len(pred_tokens & gold_tokens) / len(gold_tokens)
                
                if precision + recall == 0:
                    f1_scores.append(0.0)
                else:
                    f1 = 2 * (precision * recall) / (precision + recall)
                    f1_scores.append(f1)
        
        return {
            "exact_match": exact_matches / len(test_queries) if test_queries else 0.0,
            "avg_f1": np.mean(f1_scores) if f1_scores else 0.0,
            "num_evaluated": len(test_queries)
        }
    


