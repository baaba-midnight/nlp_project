from typing import List, Optional, Dict
from backend.app.services.ingestor import Ingest, AppDocument
from langchain_community.llms import HuggingFacePipeline
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import logging
import numpy as np

logger = logging.getLogger(__name__)

class RAGPipeline:
    def __init__(
        self,
        embedding_model: str = "sentence-transformers/all-mpnet-base-v2",
        llm_model: str = "meta-llama/Llama-2-7b-chat-hf",
        top_k: int = 4,
        use_faiss: bool = False
    ):
        # Ingestor to split and embed documents
        self.ingestor = Ingest(
            embedding_model_name=embedding_model,
            use_faiss=use_faiss
        )
        self.top_k = top_k

        # Load Llama 2 model locally
        self.tokenizer = AutoTokenizer.from_pretrained(llm_model)
        self.model = AutoModelForCausalLM.from_pretrained(llm_model)
        self.llm_pipeline = pipeline(
            task="text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            temperature=0.1,
            max_length=1024
        )
        self.llm = HuggingFacePipeline(pipeline=self.llm_pipeline)

        # Prompt template for context injection
        self.prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""
Use ONLY the context below to answer the question.

<context>
{context}
</context>

Question: {question}
"""
        )

        # Store FAISS vectorstore if using in-memory fallback
        self.faiss_store: Optional[FAISS] = None

    def ingest_document(self, doc: AppDocument) -> Dict:
        """
        Ingest a document using the existing Ingestor.
        """
        result = self.ingestor.ingest_document(doc)
        if self.ingestor.use_faiss and result.get("vectorstore"):
            self.faiss_store = result["vectorstore"]
        return result

    def _retrieve_chunks(self, query: str) -> List[str]:
        """
        Retrieve top-k relevant chunks for the query.
        """
        if self.ingestor.use_faiss and self.faiss_store:
            results = self.faiss_store.similarity_search(query, k=self.top_k)
            return [r.page_content for r in results]
        else:
            # Supabase retrieval with pgvector similarity
            from backend.app.db import supabase
            # Compute embedding
            query_embedding = self.ingestor.embedder.embed_query(query)

            # pgvector cosine similarity query
            sql = f"""
            SELECT chunk, embedding
            FROM embeddings
            ORDER BY embedding <=> {query_embedding}  -- '<=>' is cosine distance in pgvector
            LIMIT {self.top_k};
            """
            response = supabase.rpc("sql", {"query": sql}).execute()
            if response.error:
                logger.error(f"Supabase retrieval error: {response.error}")
                return []

            # Return chunk texts
            return [row["chunk"] for row in response.data]

    def ask(self, question: str) -> Dict:
        """
        RAG workflow:
        1. Retrieve top-k chunks
        2. Inject into prompt
        3. Generate answer with Llama 2
        """
        try:
            chunks = self._retrieve_chunks(question)
            context = "\n\n".join(chunks)
            prompt = self.prompt_template.format(context=context, question=question)
            
            # Generate answer
            answer = self.llm.invoke(prompt)
            
            return {
                "answer": answer,
                "sources": chunks[:self.top_k]
            }
        except Exception as e:
            logger.error(f"Error in ask method: {e}")
            raise