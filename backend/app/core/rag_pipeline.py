"""
Robust RAG Pipeline for Ghana Legal Chatbot
Now supports Google Colab API with dynamic token limits!
"""
import numpy as np
from ..core.retriever import DenseRetriever
from ..core.llm import Llama2LLM


class RAGPipeline:
    """
    Two-stage architecture:
    1. Retriever: Dense passage retrieval to find relevant documents
    2. Reader/Generator: LLM generates answer conditioned on retrieved passages
    """
    
    def __init__(self, similarity_threshold, embedder_model, language_model, 
                 use_colab_api=False, colab_url=None):
        """
        Initialize RAG pipeline with retriever and generator.
        
        Args:
            similarity_threshold: Minimum similarity for passage relevance
            embedder_model: Model name for sentence embeddings
            language_model: Model name for LLM generation
            use_colab_api: If True, use Google Colab API (recommended!)
            colab_url: Colab ngrok URL (required if use_colab_api=True)
        """
        self.similarity_threshold = similarity_threshold
        self.embedder_model = embedder_model
        self.retriever = DenseRetriever(embedder_model, similarity_threshold)
        
        # Initialize LLM (local or Colab API)
        self.llm = Llama2LLM(
            language_model,
            use_colab_api=use_colab_api,
            colab_url=colab_url
        )

   
    def build_rag_prompt(self, query, passages, max_input_length):
        """
        Construct RAG prompt with retrieved passages.
        Args:
            query: User's question
            passages: List of retrieved passages with metadata
            max_input_length: Maximum tokens for input prompt

        Returns:
            Formatted prompt string for LLM
        """
        # Build the template without passages first
        template = f"""You are a knowledgeable Ghana Legal and Climate Assistant. Your task is to answer questions accurately based ONLY on the provided legal documents.

RETRIEVED LEGAL PASSAGES:
{{passages}}

Based on these texts, answer the question below.

QUESTION: {query}

ANSWER:"""
        
        # Count tokens for everything EXCEPT passages
        template_without_passages = template.replace("{passages}", "")
        overhead_tokens = len(self.llm.tokenizer.encode(template_without_passages))
        
        # Calculate how much space is LEFT for passages
        max_context_tokens = max_input_length - overhead_tokens
        
        # Now add passages up to this calculated limit
        context_parts = []
        total_tokens = 0
        
        for idx, passage in enumerate(passages, 1):
            chunk_text = passage.get("chunk", "")
            if not chunk_text:
                continue
            
            chunk_tokens = len(self.llm.tokenizer.encode(chunk_text))
            
            if total_tokens + chunk_tokens > max_context_tokens:
                print(f"Stopping at passage {idx} to stay within token limit")
                break
            
            source = passage.get("document_title", "Unknown Document")
            context_parts.append(f"[Passage {idx} - Source: {source}]\n{chunk_text}")
            total_tokens += chunk_tokens
        
        context_text = "\n\n".join(context_parts)
        prompt = template.replace("{passages}", context_text)
        
        return prompt

    
    def run(self, query, k):
        """
        Execute complete RAG pipeline: retrieve then generate.
        
        Args:
            query: User's question
            k: Number of passages to retrieve            
        Returns:
            Dict containing answer, sources, has_chunks, and metadata
        """
        # Use model's dynamic limits 
        max_input_length = self.llm.get_max_input_length()        
        
        # Handle empty or invalid queries
        if not query or not query.strip():
            return {
                "answer": "",
                "num_sources": 0,
                "sources": [],
                "has_chunks":  False,
                "avg_similarity": 0.0
            }
        # Handle invalid k
        if k <= 0:
            print("Invalid value of k provided to RAG pipeline.")
            return {
                "answer": "",
                "num_sources": 0,
                "sources": [],
                "has_chunks": False,
                "avg_similarity": 0.0
            }
        # Stage 1: RETRIEVER
        passages = self.retriever.retrieve(query, k)
        
        # Fallback on model only if no passages found
        if not passages:
            print('Falling back on LLM-only response due to no retrieved passages.')
            fallback_prompt = f"""You are a knowledgeable Ghana Legal and Climate Assistant. 
No specific legal documents were found for this query, but please provide a helpful general answer based on your knowledge of Ghana law.

QUESTION: {query}

ANSWER:"""
            raw_answer = self.llm.generate(fallback_prompt)
            return {
                "answer": raw_answer,
                "num_sources": 0,
                "sources": [],
                "has_chunks": False,
                "avg_similarity": 0.0
            }
        
        # Stage 2: READER/GENERATOR (RAG)
        rag_prompt = self.build_rag_prompt(query, passages, max_input_length)
        
        raw_answer = self.llm.generate(rag_prompt)
        
        # Prepare response
        response = {
            "answer": raw_answer,
            "sources": passages,
            "has_chunks": True,
            "num_sources": len(passages),
            "avg_similarity": np.mean([p["similarity"] for p in passages])
        }
        return response