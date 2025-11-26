"""
Robust RAG Pipeline for Ghana Legal Chatbot
"""
from typing import Dict, List
from app.core.retriever import Retriever
from app.core.llm import Llama2LLM



class RAGPipeline:
    def __init__(self, use_faiss=False, faiss_store=None, similarity_threshold: float = 0.65):
        self.retriever = Retriever(use_faiss=use_faiss, faiss_store=faiss_store)
        self.llm = Llama2LLM()
        self.similarity_threshold = similarity_threshold

    def filter_relevant_chunks(self, chunks: List[Dict]):
        """
        Filter retrieved chunks by embedding similarity.
        Ensures similarity is converted to float even if Supabase returns it as a string.
        """
        cleaned = []

        for c in chunks:
            sim_raw = c.get("similarity", 0.0)
            similarity = float(sim_raw)

            c["similarity"] = similarity   
            cleaned.append(c)

        # Now filter correctly
        relevant = [c for c in cleaned if c["similarity"] >= self.similarity_threshold]

        # Sort descending by similarity
        relevant_sorted = sorted(relevant, key=lambda x: x["similarity"], reverse=True)

        return relevant_sorted


    def build_prompt(self, query: str, contexts: List[Dict], max_tokens: int = 2000) -> str:
        """
        Construct the prompt for the LLM.
        Ensures chunks fit within token limits (simplified truncation here).
        """
        context_text = ""
        total_tokens = 0

        for idx, c in enumerate(contexts):
            chunk_text = c.get("chunk", "")
            # Simplified token count: 1 token ~ 1 word (approximation)
            chunk_tokens = len(chunk_text.split())
            if total_tokens + chunk_tokens > max_tokens:
                break
            context_text += f"\nChunk {idx+1}:\n{chunk_text}\n"
            total_tokens += chunk_tokens

        prompt = f"""You are a Ghana Legal Assistant. ONLY answer based on the CONTEXT below.

CRITICAL RULES:
1. Use ONLY the information in the context.
2. Do NOT use knowledge outside the context.
3. If answer is not in context, respond: "I cannot answer this question based on the provided documents."
4. Cite chunks where appropriate.

CONTEXT:
{context_text}

QUESTION: {query}

FINAL ANSWER:"""
        return prompt

    def run(self, query, k):
        # Step 1: Embed + retrieve top K chunks
        chunks = self.retriever.retrieve(query, k*2) 
        if not chunks:
            return {
                "answer": "I couldn't find any relevant documents in the database.",
                "sources": [],
                "error": "no_results"
            }

        # Step 2: Filter by similarity (requires chunks to include similarity score)
        filtered_chunks = self.filter_relevant_chunks(chunks)

        if not filtered_chunks:
            return {
                "answer": f"I don't have information about '{query}' in my database.",
                "sources": chunks,
                "error": "irrelevant_context"
            }

        # Step 3: Build prompt
        prompt = self.build_prompt(query, filtered_chunks)

        # Step 4: Generate answer
        raw_output = self.llm.generate(prompt, max_new_tokens=300)

        # Step 5: Extract final answer
        if "FINAL ANSWER:" in raw_output:
            answer = raw_output.split("FINAL ANSWER:")[-1].strip()
        else:
            answer = raw_output.strip()

        # Step 6: Detect uncertainty
        uncertainty_phrases = [
            "i cannot answer",
            "i don't have",
            "not in the context",
            "cannot find",
            "not provided",
            "no information"
        ]
        warning = None
        if any(phrase in answer.lower() for phrase in uncertainty_phrases):
            warning = "llm_uncertain"

        # Step 7: Return structured response
        return {
            "answer": answer,
            "sources": filtered_chunks,
            "warning": warning
        }