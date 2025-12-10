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

# ...existing code...
import logging
import os
import tempfile
from typing import Any, List

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from pydantic import BaseModel

router = APIRouter(prefix="/upload", tags=["upload"])
logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.INFO)


class URLPayload(BaseModel):
    url: str


def _lazy_services():
    try:
        from ..services.loaders.hybrid_loader import HybridPDFLoader
        from ..services.ingestor import Ingest
        from ..services.scrapers.web_scraper import WebScraperService

        return HybridPDFLoader, Ingest, WebScraperService
    except Exception as exc:
        raise RuntimeError(f"Missing ingestion services: {exc}")


@router.post("/process/url", summary="Submit a URL (JSON)")
async def process_url(payload: URLPayload) -> dict:
    logger.info("process_url called; url=%s", payload.url)
    if not payload.url.startswith(("http://", "https://")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provided URL is invalid. It must start with http:// or https://",
        )

    _, Ingest, WebScraperService = _lazy_services()

    scraper = WebScraperService()
    try:
        doc = scraper.scrape_url(payload.url)
    except Exception as e:
        logger.exception("Error scraping URL: %s", payload.url)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error scraping URL {payload.url}: {e}",
        )

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Scraper returned no document for URL: {payload.url}",
        )

    ingestor = Ingest(use_faiss=False)
    try:
        res = ingestor.ingest_document(doc)
    except Exception as exc:
        logger.exception("Ingest failed for URL document")
        res = {"status": "error", "error": str(exc), "chunks": 0}

    total_chunks = int(res.get("chunks", 0) or 0)
    errors = [res] if res.get("status") != "ok" else []

    return {
        "status": "ok" if not errors else "partial",
        "documents": 1,
        "chunks": total_chunks,
        "errors": errors,
        "results": [res],
    }


@router.post("/process/" \
"file", summary="Upload file(s) (multipart/form-data)")
async def process_files(files: List[UploadFile] = File(...)) -> dict:
    logger.info("process_files called; files_count=%d", len(files) if files else 0)
    HybridPDFLoader, Ingest, WebScraperService = _lazy_services()

    documents: List[Any] = []
    for upload in files:
        if not hasattr(upload, "filename") or not callable(getattr(upload, "read", None)):
            logger.warning("Skipping invalid upload value: %r", upload)
            continue

        filename = getattr(upload, "filename", "") or ""
        content_type = getattr(upload, "content_type", None)
        logger.info("Processing upload: filename=%s content_type=%s", filename, content_type)

        try:
            data = await upload.read()
        except Exception:
            logger.exception("Failed to read upload: %s", filename)
            try:
                await upload.close()
            except Exception:
                pass
            continue
        finally:
            try:
                await upload.close()
            except Exception:
                pass

        is_pdf = False
        try:
            if content_type == "application/pdf":
                is_pdf = True
            elif filename.lower().endswith(".pdf"):
                is_pdf = True
            elif isinstance(data, (bytes, bytearray)) and data[:4] == b"%PDF":
                is_pdf = True
        except Exception:
            is_pdf = False

        if is_pdf:
            tmp_path = None
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(data)
                    tmp_path = tmp.name

                loader = HybridPDFLoader()
                try:
                    docs = loader.load_pdf(tmp_path)
                except Exception:
                    logger.exception("PDF loader failed for file: %s", filename)
                    docs = None
                if docs:
                    documents.extend(docs)
            finally:
                if tmp_path and os.path.exists(tmp_path):
                    try:
                        os.unlink(tmp_path)
                    except Exception:
                        pass
        else:
            text = ""
            try:
                text = data.decode("utf-8").strip()
            except Exception:
                text = ""
            if text.startswith(("http://", "https://")):
                logger.info("File body contains URL, scraping: %s", text)
                scraper = WebScraperService()
                try:
                    doc = scraper.scrape_url(text)
                except Exception:
                    logger.exception("Failed scraping URL from file body: %s", text)
                    doc = None
                if doc:
                    documents.append(doc)
            else:
                logger.info("Skipping non-pdf non-url file: %s", filename)

    if not documents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid documents were extracted from uploaded files.",
        )

    ingestor = Ingest(use_faiss=False)
    results = []
    for doc in documents:
        try:
            res = ingestor.ingest_document(doc)
        except Exception as exc:
            logger.exception("Ingest failed for a document")
            res = {"status": "error", "error": str(exc), "chunks": 0}
        results.append(res)

    total_chunks = sum(int(r.get("chunks", 0) or 0) for r in results)
    errors = [r for r in results if r.get("status") != "ok"]

    return {
        "status": "ok" if not errors else "partial",
        "documents": len(documents),
        "chunks": total_chunks,
        "errors": errors,
        "results": results,
    }
