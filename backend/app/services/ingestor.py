"""
File: ingestor.py
Project: services
File Created: Tuesday, 18th November 2025 8:36:35 PM
Author: baaba-midnight
Email: baaba.amosah@gmail.com
Version: 1.0
Brief: <<brief>>
-----
Last Modified: Tuesday, 18th November 2025 9:22:58 PM
Modified By: baaba-midnight
-----
Copyright ©2025 baaba-midnight
"""

from typing import Optional, List, Union
from sqlalchemy import create_engine

# langchain imports
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document as LCDocument
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import PGVector, FAISS

# local dataclasses
from .ingestion import Document as AppDocument

class Ingestor:
    """
    Ingestor class for processing and storing documents in vector databases.
    Accepts AppDocument instances, splits them into chunks, generates embeddings,
    """

    def __init__(
            self, 
            chunk_size: int = 1000,
            chunk_overlap: int = 200,
            embedding_model_name: str = "all-MiniLM-L6-v2",
            pg_dsn: Optional[str] = None,
            pg_table_name: str = "embeddings",
            use_faiss: bool = False
    ):  
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.embedder = SentenceTransformerEmbeddings(model_name=embedding_model_name)
        self.pg_dsn = pg_dsn
        self.pg_table_name = pg_table_name
        self.use_faiss = use_faiss
        
    def _to_langchain_docs(self, doc: Union[AppDocument, dict]) -> List[LCDocument]:
        # Convert AppDocument or dict to LangChain Document
        if isinstance(doc, AppDocument):
           text = doc.text
           metadata = doc.metadata 
           metadata.update({"title": doc.title, "source": doc.source})
        else:
            text = doc.get("text", "") or ""
            metadata = doc.get("metadata", {})
            metadata.update({"title": doc.get("title", ""), "source": doc.get("source", "")})

        lc_doc = LCDocument(page_content=text, metadata=metadata)
        return self.splitter.split_documents([lc_doc]) # split langchain document into chunks
    
    def ingest(self, doc: Union[AppDocument, dict]) -> dict:
        """
        Splits, embeds, and persists the document into the vector database.
        Returns a dict with summary and the vectorstore object (if created)
        """
        lc_docs = self._to_langchain_docs(doc)
        if not lc_docs:
            return {"status": "empty document", "chunks": 0}
        
        # choose persistence method: postgres or faiss
        if self.pg_dsn and not self.use_faiss:
            engine = create_engine(self.pg_dsn)
            store = PGVector.from_documents(lc_docs, self.embedder, engine=engine, collection_name=self.pg_table_name)
            return {"status": "ok", "chunks": len(lc_docs), "vectorstore": store}
        else:
            store = FAISS.from_documents(lc_docs, self.embedder)
            return {"status": "ok", "chunks": len(lc_docs), "vectorstore": store}