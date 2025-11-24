"""
RAG Pipeline Orchestrator for Ghana Legal Chatbot
"""
from typing import Dict, List
from app.core.retriever import Retriever
from app.core.llm import Llama2LLM


class RAGPipeline:
    def __init__(self, use_faiss=False, faiss_store=None):
        self.retriever = Retriever(use_faiss=use_faiss, faiss_store=faiss_store)
        self.llm = Llama2LLM()

    def build_prompt(self, query: str, contexts: List[Dict]) -> str:
        context_text = "\n\n".join(
            [c["chunk"] if "chunk" in c else c.page_content for c in contexts]
        )

        return f"""
You are a Ghana Legal Assistant.
You must answer using ONLY the following context from Ghana legal documents.

<context>
{context_text}
</context>

Question: {query}

If the answer is not present in the context, say:
"I couldn't find any information in the provided legal documents."
"""

    def run(self, query: str, k: int = 4) -> Dict:
        # Retrieve chunks
        chunks = self.retriever.retrieve(query, k)

        # Build prompt
        prompt = self.build_prompt(query, chunks)

        # Llama-2 generation
        answer = self.llm.generate(prompt)

        return {
            "answer": answer,
            "sources": chunks
        }