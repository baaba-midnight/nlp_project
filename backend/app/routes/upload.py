"""File: upload.py
Project: routes
File Created: Wednesday, 26th November 2025 12:26:46 PM
Author: baaba-midnight
Email: baaba.amosah@gmail.com
Version: 1.0
Brief: <<brief>>
-----
Last Modified: Wednesday, 26th November 2025 12:51:41 PM
Modified By: baaba-midnight
-----
Copyright ©2025 baaba-midnight
"""

import os
import tempfile
from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile

from ..services.hybrid_loader import HybridPDFLoader
from ..services.ingestor import Ingest
from ..services.web_scraper import WebScraperService

router = APIRouter()


@router.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    documents = []
    for upload in files:
        # handle PDF uploads: write to temp file then use HybridPDFLoader
        if upload.content_type == "application/pdf":
            try:
                data = await upload.read()
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(data)
                    tmp_path = tmp.name

                loader = HybridPDFLoader()
                docs = loader.load_pdf(tmp_path)
                if docs:
                    documents.extend(docs)
            finally:
                # cleanup temp file
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

        # handle simple URL uploads (client posted a plain URL in file body)
        elif upload.content_type in ("text/url", "text/plain", "text/uri-list"):
            url = (await upload.read()).decode("utf-8").strip()
            if not url:
                continue
            scraper = WebScraperService()
            doc = scraper.scrape_url(url)
            if doc:
                documents.append(doc)

        else:
            # skip unknown / binary types
            continue

    if not documents:
        raise HTTPException(
            status_code=400, detail="No valid documents were provided or extracted."
        )

    ingestor = Ingest(use_faiss=False)
    results = []
    for doc in documents:
        res = ingestor.ingest_document(doc)
        results.append(res)

    # aggregate results
    total_chunks = sum(r.get("chunks", 0) for r in results)
    errors = [r for r in results if r.get("status") != "ok"]

    return {
        "status": "ok" if not errors else "partial",
        "documents": len(documents),
        "chunks": total_chunks,
        "errors": errors,
        "results": results,
    }
