"""
Robust RAG Pipeline for Ghana Legal Chatbot
"""

from typing import Dict, List, Tuple, Optional
import numpy as np
from ..core.retriever import DenseRetriever
from ..core.llm import Llama2LLM


class RAGPipeline:
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
        self.retriever = DenseRetriever(use_faiss=use_faiss, faiss_store=faiss_store)
        # Initialize LLM for generation
        self.llm = Llama2LLM()


    def filter_relevant_passages(self, passages: List[Dict]) -> List[Dict]:
        """
        Filter passages by similarity threshold.
        Helps ensure retrieved passages are actually relevant (Section 14.1.4).
        """
        if not passages:
            return []
        
        relevant = []
        for passage in passages:
            similarity = float(passage.get("similarity", 0.0))
            passage["similarity"] = similarity
            if similarity >= self.similarity_threshold:
                relevant.append(passage)
        # Sort by similarity (descending)
        relevant_sorted = sorted(relevant, key=lambda x: x["similarity"], reverse=True)
        print(f"Filtered {len(relevant_sorted)}/{len(passages)} passages above threshold {self.similarity_threshold}")
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
                print(f"Stopping at passage {idx} to stay within token limit")
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
        if not query or not query.strip():
            return {
                "answer": "Please provide a valid question.",
                "sources": [],
                "confidence": 0.0,
                "error": "empty_query"
            }
        if k<=0:
            k=5
        # Stage 1: RETRIEVAL
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
        top_passages = relevant_passages[:k]
        # Stage 2: READER/GENERATOR (RAG)
        rag_prompt = self.build_rag_prompt(query, top_passages)
            
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
        print(f"[COMPLETE] Answer generated with {len(top_passages)} sources (confidence: {confidence:.2f})")
        return response
    
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