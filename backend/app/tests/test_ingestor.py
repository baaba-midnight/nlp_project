"""
File: test_ingestor.py
Project: tests
File Created: Tuesday, 18th November 2025 9:00:37 PM
Author: baaba-midnight
Email: baaba.amosah@gmail.com
Version: 1.0
Brief: <<brief>>
-----
Last Modified: Saturday, 22nd November 2025 4:01:23 PM
Modified By: baaba-midnight
-----
Copyright ©2025 baaba-midnight
"""

from backend.app.services.ingestor import Ingest
from app.services.ingestion import Document as AppDocument
from langchain_community.vectorstores import FAISS as FAISSClass

import os
import json
import logging

logging.basicConfig(level=logging.INFO)

ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "test")
)


def load_json(name):
    path = os.path.join(ROOT, name)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_text(name):
    path = os.path.join(ROOT, name)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class DummyEmbedder:
    """Return fixed-dimension zero vectors to avoid real model calls."""

    def embed_documents(self, texts):
        # mimic all-MiniLM-L6-v2 (384 dims)
        return [[0.0] * 384 for _ in texts]


def main():
    print("Looking for test data in:", ROOT)

    # monkeypatch FAISS to avoid needing faiss installation
    FAISSClass.from_documents = staticmethod(lambda documents, embedding: "FAISS_MOCK")

    # load a small JSON-backed test doc
    dd = load_json("dict_doc.json")
    app_doc = AppDocument(
        source=dd["source"],
        title=dd["title"],
        text=dd["text"],
        metadata=dd.get("metadata", {}),
    )

    ingest = Ingest(use_faiss=False, chunk_size=200, chunk_overlap=20)
    # replace real embedder with dummy
    ingest.embedder = DummyEmbedder()

    res = ingest.ingest_document(app_doc)
    print("DICT_DOC -> status:", res.get("status"), "chunks:", res.get("chunks"))

    # also test a long text file
    long_txt = load_text("long_judgment.txt")
    long_doc = AppDocument(
        source="local/long_judgment.txt",
        title="Long Judgment",
        text=long_txt,
        metadata={"category": "judgment"},
    )
    res2 = ingest.ingest_document(long_doc)
    print("LONG_JUDGMENT -> status:", res2.get("status"), "chunks:", res2.get("chunks"))


if __name__ == "__main__":
    main()
