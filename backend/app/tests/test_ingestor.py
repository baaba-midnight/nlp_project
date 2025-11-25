"""
File: test_ingestor.py
Project: tests
File Created: Tuesday, 18th November 2025 9:00:37 PM
Author: baaba-midnight
Email: baaba.amosah@gmail.com
Version: 1.0
Brief: <<brief>>
-----
Last Modified: Tuesday, 25th November 2025 9:36:50 PM
Modified By: baaba-midnight
-----
Copyright ©2025 baaba-midnight
"""

import json
import logging
import os

from langchain_community.vectorstores import FAISS as FAISSClass
from langchain_core.documents import Document

from backend.app.services.ingestor import Ingest
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

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
        # Return deterministic non-zero vectors derived from sha256 of text.
        # This avoids external model calls but gives varied embeddings for tests.
        import hashlib

        dim = 384
        vectors = []
        for t in texts:
            h = hashlib.sha256(t.encode("utf-8")).digest()
            # expand bytes into floats in [0,1]
            vec = [float(h[i % len(h)]) / 255.0 for i in range(dim)]
            vectors.append(vec)
        return vectors


def main():
    print("Looking for test data in:", ROOT)

    # monkeypatch FAISS to avoid needing faiss installation
    FAISSClass.from_documents = staticmethod(lambda documents, embedding: "FAISS_MOCK")

    # load a small JSON-backed test doc
    dd = load_json("dict_doc.json")
    app_doc = Document(
        page_content=dd["text"],
        metadata={
            "source": dd["source"],
            "title": dd["title"],
            **dd.get("metadata", {}),
        },
    )

    ingest = Ingest(use_faiss=False, chunk_size=200, chunk_overlap=20)
    # replace real embedder with dummy
    ingest.embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    res = ingest.ingest_document(app_doc)
    print("DICT_DOC -> status:", res.get("status"), "chunks:", res.get("chunks"))

    # also test a long text file
    long_txt = load_text("long_judgment.txt")
    long_doc = Document(
        page_content=long_txt,
        metadata={
            "source": "local/long_judgment.txt",
            "title": "Long Judgment",
            "category": "judgment",
        },
    )
    res2 = ingest.ingest_document(long_doc)
    print("LONG_JUDGMENT -> status:", res2.get("status"), "chunks:", res2.get("chunks"))


if __name__ == "__main__":
    main()
