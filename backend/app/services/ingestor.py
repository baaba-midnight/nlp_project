"""
File: ingestor.py
Project: services
File Created: Tuesday, 18th November 2025 8:36:35 PM
Author: baaba-midnight
Email: baaba.amosah@gmail.com
Version: 1.0
Brief: <<brief>>
-----
Last Modified: Tuesday, 25th November 2025 9:36:27 PM
Modified By: baaba-midnight
-----
Copyright ©2025 baaba-midnight
"""

import logging  # for logging errors and info
from typing import List, Optional, TypedDict, Union

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.app.db import supabase

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
    Accepts langchain Document instances (single or list), splits them into chunks, generates embeddings,
    and stores them either in Supabase (with pgvector) or FAISS.
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        embedding_model_name: str = "all-MiniLM-L6-v2",
        use_faiss: bool = False,
        model_kwargs: Optional[dict] = None,
    ):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

        # allow passing model kwargs (e.g. {"device": "cpu"} or {"device": "cuda"})
        if model_kwargs is None:
            model_kwargs = {}
        self.embedder = HuggingFaceEmbeddings(
            model_name=embedding_model_name, model_kwargs=model_kwargs
        )
        self.use_faiss = use_faiss
        logger.info(
            f"Ingest initialized with {'FAISS' if use_faiss else 'Supabase'} backend."
        )

    def _normalize_and_split(
        self, docs: Union[Document, List[Document]]
    ) -> List[Document]:
        """
        Normalize input into a list of langchain Document instances and split into chunks using splitter.
        - If a single document is passed, wrap and split
        - If a list is passed, splitter will further split each document in the list.
        """
        if docs is None:
            return []
        if isinstance(docs, Document):
            docs = [docs]
        elif not isinstance(docs, list):
            docs = docs
        else:
            logger.error("Unsupported document type provided for ingestion.")
            return []

        # split documents into chunks
        try:
            splitted = self.splitter.split_documents(docs)
            return splitted
        except Exception as e:
            logger.error(f"Error during document splitting: {e}")
            return docs

    def _ingest_to_supabase(
        self, lc_doc: List[Document], embeddings: List[List[float]]
    ) -> IngestResult:
        """Ingest langchain documents into Supabase"""
        try:
            if not lc_doc:
                raise ValueError("No document chunks provided for Supabase ingestion.")

            first_meta = lc_doc[0].metadata or {}
            doc_payload = {
                "source": first_meta.get("source", ""),
                "title": first_meta.get("title", ""),
                "metadata": first_meta,
            }

            # upsert documents
            logger.info(f"Upserting document: {doc_payload['title']}")
            doc_response = supabase.table("documents").upsert(doc_payload).execute()

            if not doc_response.data or len(doc_response.data) == 0:
                logger.error(
                    "Failed to upsert document to Supabase - no data returned."
                )

                return {
                    "status": "error",
                    "chunks": 0,
                    "document_id": None,
                    "vectorstore": None,
                    "error": "Failed to upsert document to Supabase.",
                }

            document_id = doc_response.data[0]["id"]
            logger.info(f"Document upsert with ID: {document_id}")

            # prepare chunks payload
            rows = []
            for idx, (chunk_doc, embedding) in enumerate(zip(lc_doc, embeddings)):
                rows.append({
                    "document_id": document_id,
                    "chunk_index": idx,
                    "chunk": chunk_doc.page_content,
                    "metadata": chunk_doc.metadata,
                    "embedding": embedding,
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
                "chunks": len(lc_doc),
                "document_id": document_id,
                "vectorstore": None,
                "error": None,
            }
        except Exception as e:
            logger.error(f"Error ingesting to Supabase: {e}")
            return {
                "status": "error",
                "chunks": 0,
                "document_id": None,
                "vectorstore": None,
                "error": str(e),
            }

    def _ingest_to_faiss(self, lc_doc: List[Document]) -> IngestResult:
        """Ingest documents into FAISS"""
        try:
            logger.info(f"Creating FAISS vectorstore with {len(lc_doc)} documents.")
            vectorstore = FAISS.from_documents(
                documents=lc_doc, embedding=self.embedder
            )

            logger.info(f"Successfully ingested {len(lc_doc)} chunks into FAISS.")
            return {
                "status": "ok",
                "chunks": len(lc_doc),
                "document_id": None,
                "vectorstore": vectorstore,
                "error": None,
            }
        except Exception as e:
            logger.error(f"Error ingesting to FAISS: {e}")
            return {
                "status": "error",
                "chunks": 0,
                "document_id": None,
                "vectorstore": None,
                "error": str(e),
            }

    def ingest_document(self, lc_doc: Document) -> IngestResult:
        """
        Splits, embeds, and persists the document into the vector database
        Returns a dict with status, chunk count, and either document_id or vectorstore.
        """
        try:
            lc_doc = self._normalize_and_split(lc_doc)
            if not lc_doc:
                logger.warning("No document chunks were created during splitting.")
                return {
                    "status": "error",
                    "chunks": 0,
                    "document_id": None,
                    "vectorstore": None,
                    "error": "No document chunks created.",
                }

            logger.info(f"Document split into {len(lc_doc)} chunks.")

            # Generate embeddings for all chunks
            texts = [d.page_content for d in lc_doc]
            embeddings = self.embedder.embed_documents(texts)

            # route to appropriate ingestion method
            if self.use_faiss:
                return self._ingest_to_faiss(lc_doc)
            else:
                return self._ingest_to_supabase(lc_doc, embeddings)
        except Exception as e:
            logger.error(f"Error during document ingestion: {e}")
            return {
                "status": "error",
                "chunks": 0,
                "document_id": None,
                "vectorstore": None,
                "error": str(e),
            }
