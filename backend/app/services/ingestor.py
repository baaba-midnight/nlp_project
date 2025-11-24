"""
File: ingestor.py
Project: services
File Created: Tuesday, 18th November 2025 8:36:35 PM
Author: baaba-midnight
Email: baaba.amosah@gmail.com
Version: 1.0
Brief: <<brief>>
-----
Last Modified: Monday, 24th November 2025 7:29:29 PM
Modified By: baaba-midnight
-----
Copyright ©2025 baaba-midnight
"""

from typing import List, Union, Optional, TypedDict
from backend.app.db import supabase
import logging  # for logging errors and info

# langchain imports
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document as LCDocument
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from .ingestion import Document as AppDocument

# setup loggin
logger = logging.getLogger(__name__)


class IngestResult(TypedDict):
    """Ingest Result TypedDict"""

    status: str
    chunks: int
    document_id: Optional[int]
    vectorstore: Optional[FAISS]
    error: Optional[str]


class Ingest:
    """
    Ingest class for processing and storing documents in vector databases.
    Accepts AppDocument instances, splits them into chunks, generates embeddings,
    and stores them either in Supabase (with pgvector) or FAISS (in-memory).
    """

    def __init__(
            self,
            chunk_size: int = 1000,
            chunk_overlap: int = 200,
            embedding_model_name: str = "all-MiniLM-L6-v2",
            use_faiss: bool = False
    ):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )   
        self.embedder = HuggingFaceEmbeddings(model_name=embedding_model_name)
        self.use_faiss = use_faiss
        logger.info(f"Ingest initialized with {'FAISS' if use_faiss else 'Supabase'} backend.")

    def _to_langchain_document(self, doc: Union[AppDocument, dict]) -> LCDocument:
        """Convert AppDocument to LangChain Document"""
        if isinstance(doc, AppDocument):
            text = doc.text
            metadata = doc.metadata
            metadata.update(
                {"title": doc.title, "source": doc.source}
            )
        else:
            text = doc.get("text", "")
            metadata = doc.get("metadata", {})
            metadata.update(
                {"title": doc.get("title", ""), "source": doc.get("source", "")}
            )

        lc_doc = LCDocument(page_content=text, metadata=metadata)
        return self.splitter.split_documents([lc_doc])
    
    def _ingest_to_supabase(
            self,
            lc_docs: List[LCDocument],
            embeddings: List[List[float]],
            doc: Union[AppDocument, dict]
    ) -> IngestResult:
        """Ingest documents into Supabase"""
        try:
            first_meta = lc_docs[0].metadata or {}
            doc_payload = {
                "source": first_meta.get("source", "") or (
                    doc.source if isinstance(doc, AppDocument) else doc.get("source", "")
                ),
                "title": first_meta.get("title", "") or (
                    doc.title if isinstance(doc, AppDocument) else doc.get("title", "")
                ),
                "metadata": first_meta,
            }

            # upsert documents
            logger.info(f"Upserting document: {doc_payload['title']}")
            doc_response = (
                supabase.table("documents")
                .upsert(doc_payload)
                .execute()
            )
        
            if not doc_response.data or len(doc_response.data) == 0:
                logger.error("Failed to upsert document to Supabase - no data returned.")

                return {
                    "status": "error",
                    "chunks": 0,
                    "document_id": None,
                    "vectorstore": None,
                    "error": "Failed to upsert document to Supabase."
                }
            
            document_id = doc_response.data[0]["id"]
            logger.info(f"Document upsert with ID: {document_id}")

            # prepare chunks payload
            rows = []
            for idx, (lc_doc, embedding) in enumerate(zip(lc_docs, embeddings)):
                rows.append({
                    "document_id": document_id,
                    "chunk_index": idx,
                    "chunk": lc_doc.page_content,
                    "metadata": lc_doc.metadata,
                    "embedding": embedding
                })
                
            # upsert chunks
            logger.info(f"Upserting {len(rows)} embedding chunks to Supabase.")
            (
                supabase.table("embeddings")
                .upsert(rows, on_conflict="document_id, chunk_index")
                .execute()
            )

            logger.info(f"Successfully ingested {len(rows)} chunks into Supabase.")
            return {
                "status": "ok",
                "chunks": len(lc_docs),
                "document_id": document_id,
                "vectorstore": None,
                "error": None
            }
        except Exception as e:
            logger.error(f"Error ingesting to Supabase: {e}")
            return {
                "status": "error",
                "chunks": 0,
                "document_id": None,
                "vectorstore": None,
                "error": str(e)
            }
        
    def _ingest_to_faiss(
            self,
            lc_docs: List[LCDocument]
    ) -> IngestResult:
        """Ingest documents into FAISS"""
        try:
            logger.info(f"Creating FAISS vectorstore with {len(lc_docs)} documents.")
            vectorstore = FAISS.from_documents(
                documents=lc_docs,
                embedding=self.embedder
            )
            
            logger.info(f"Successfully ingested {len(lc_docs)} chunks into FAISS.")
            return {
                "status": "ok",
                "chunks": len(lc_docs),
                "document_id": None,
                "vectorstore": vectorstore,
                "error": None
            }
        except Exception as e:
            logger.error(f"Error ingesting to FAISS: {e}")
            return {
                "status": "error",
                "chunks": 0,
                "document_id": None,
                "vectorstore": None,
                "error": str(e)
            }
    
    def ingest_document(self, doc: Union[AppDocument, dict]) -> IngestResult:
        """
        Splits, embeds, and persists the document into the vector database
        Returns a dict with status, chunk count, and either document_id or vectorstore.
        """
        try:
            # Convert to langchain document and split
            lc_docs = self._to_langchain_document(doc)

            if not lc_docs:
                logger.warning("No document chunks were created during splitting.")
                return {
                    "status": "error",
                    "chunks": 0,
                    "document_id": None,
                    "vectorstore": None,
                    "error": "No document chunks created."
                }
            
            logger.info(f"Document split into {len(lc_docs)} chunks.")

            # Generate embeddings for all chunks
            texts = [d.page_content for d in lc_docs]
            embeddings = self.embedder.embed_documents(texts)

            # route to appropriate ingestion method
            if self.use_faiss:
                return self._ingest_to_faiss(lc_docs)
            else:
                return self._ingest_to_supabase(lc_docs, embeddings, doc)
        except Exception as e:
            logger.error(f"Error during document ingestion: {e}")
            return {
                "status": "error",
                "chunks": 0,
                "document_id": None,
                "vectorstore": None,
                "error": str(e)
            }