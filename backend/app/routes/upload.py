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

import asyncio
import os
import tempfile
from typing import Any, List

from ..services.hybrid_loader import HybridPDFLoader
from ..services.ingestor import Ingest
from ..services.web_scraper import WebScraperService


def _read_bytes_from_upload(upload: Any) -> bytes:
    """Attempt to read bytes from a file-like upload object or return bytes if input is bytes.

    Supports:
    - objects with a synchronous `.read()` method (typical in Streamlit)
    - objects with an async `.read()` (will be run)
    - raw bytes
    - strings (will be encoded)
    """
    if isinstance(upload, bytes):
        return upload
    if isinstance(upload, str):
        return upload.encode("utf-8")

    read = getattr(upload, "read", None)
    if callable(read):
        # handle async or sync
        if asyncio.iscoroutinefunction(read):
            return asyncio.run(read())
        data = read()
        # some wrappers (e.g., io.BytesIO) return str/bytes
        if isinstance(data, str):
            return data.encode("utf-8")
        return data

    # fallback: try to get value attribute for Streamlit's UploadedFile
    getvalue = getattr(upload, "getvalue", None)
    if callable(getvalue):
        return getvalue()

    raise ValueError("Cannot read uploaded file-like object")


def process_uploads(files: List[Any]):
    """Process uploaded files or URLs and ingest documents.

    `files` may contain file-like objects (with `.read()`), raw bytes, or URL strings.
    Returns an aggregate result dict similar to the original endpoint.
    """
    documents = []
    for upload in files:
        # if a plain URL string was provided
        if isinstance(upload, str) and upload.startswith(("http://", "https://")):
            scraper = WebScraperService()
            doc = scraper.scrape_url(upload)
            if doc:
                documents.append(doc)
            continue

        # read bytes from upload
        try:
            data = _read_bytes_from_upload(upload)
        except Exception:
            # skip unreadable items
            continue

        # try to detect PDF by filename or simple magic header
        filename = getattr(upload, "name", "") or getattr(upload, "filename", "")
        content_type = getattr(upload, "content_type", None) or getattr(
            upload, "type", None
        )

        is_pdf = False
        if content_type == "application/pdf":
            is_pdf = True
        elif filename.lower().endswith(".pdf"):
            is_pdf = True
        elif data[:4] == b"%PDF":
            is_pdf = True

        if is_pdf:
            tmp_path = None
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(data)
                    tmp_path = tmp.name

                loader = HybridPDFLoader()
                docs = loader.load_pdf(tmp_path)
                if docs:
                    documents.extend(docs)
            finally:
                if tmp_path:
                    try:
                        os.unlink(tmp_path)
                    except Exception:
                        pass
        else:
            # treat as potential URL in file body
            try:
                text = data.decode("utf-8").strip()
            except Exception:
                text = ""
            if text.startswith(("http://", "https://")):
                scraper = WebScraperService()
                doc = scraper.scrape_url(text)
                if doc:
                    documents.append(doc)
            else:
                # skip unknown types for now
                continue

    if not documents:
        raise ValueError("No valid documents were provided or extracted.")

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
