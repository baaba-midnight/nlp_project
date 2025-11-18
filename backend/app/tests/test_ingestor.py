"""
File: test_ingestor.py
Project: tests
File Created: Tuesday, 18th November 2025 9:00:37 PM
Author: baaba-midnight
Email: baaba.amosah@gmail.com
Version: 1.0
Brief: <<brief>>
-----
Last Modified: Tuesday, 18th November 2025 9:25:50 PM
Modified By: baaba-midnight
-----
Copyright ©2025 baaba-midnight
"""
import os
import json
from app.services.ingestor import Ingestor
from app.services.ingestion import Document as AppDocument

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "test"))

def load_json(name):
    path = os.path.join(ROOT, name)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
    
def load_text(name):
    path = os.path.join(ROOT, name)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
    

def main():
    print("Looking for test data in:", ROOT)
    # load dict_doc.json (present in generated test data)
    dd = load_json("dict_doc.json")
    app_doc = AppDocument(source=dd["source"], title=dd["title"], text=dd["text"], metadata=dd.get("metadata", {}))

    # init ingestor with FAISS fallback so Postgres is not required
    ingestor = Ingestor(use_faiss=True)
    res = ingestor.ingest(app_doc)
    print("DICT_DOC -> status:", res.get("status"), "chunks:", res.get("chunks"))

    # also test a long text file
    long_txt = load_text("long_judgment.txt")
    long_doc = AppDocument(source="local/long_judgment.txt", title="Long Judgment", text=long_txt, metadata={"category": "judgment"})
    res2 = ingestor.ingest(long_doc)
    print("LONG_JUDGMENT -> status:", res2.get("status"), "chunks:", res2.get("chunks"))

if __name__ == "__main__":
    main()
