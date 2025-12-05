"""
Example usage of the preprocessing services.

This script demonstrates how to use the PDF loader, OCR loader, hybrid loader,
web scraper, and text cleaner.

To run this script:
    cd backend
    python -m app.services.example_usage

Or from the project root:
    python -m backend.app.services.example_usage
"""

import logging
import sys
from pathlib import Path

# Add backend directory to path if running script directly
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from ..utils.text_cleaner import TextCleaner
from .loaders.hybrid_loader import HybridPDFLoader
from .loaders.ocr_loader import OCRLoaderService
from .loaders.pdf_loader import PDFLoaderService
from .scrapers.web_scraper import WebScraperService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Example usage of preprocessing services."""

    # Initialize services
    pdf_loader = PDFLoaderService()
    ocr_loader = OCRLoaderService()
    hybrid_loader = HybridPDFLoader()
    web_scraper = WebScraperService()
    text_cleaner = TextCleaner()

    # Example 1: Load from local file (manual detection)
    local_pdf = Path(__file__).parent.parent / "data" / "companies_Act.pdf"

    if local_pdf.exists():
        logger.info(f"Loading PDF from: {local_pdf}")

        # Check if scanned
        is_scanned = pdf_loader.is_scanned_pdf(str(local_pdf))
        logger.info(f"PDF is scanned: {is_scanned}")

        if is_scanned:
            # Use OCR for scanned PDFs
            logger.info("Using OCR loader for scanned PDF")
            documents = ocr_loader.load_pdf(str(local_pdf))
        else:
            # Use regular PDF loader for native PDFs
            logger.info("Using regular PDF loader for native PDF")
            documents = pdf_loader.load_from_local(str(local_pdf))

        # Clean the documents
        logger.info("Cleaning documents...")
        cleaned_documents = text_cleaner.clean_documents(documents)

        logger.info(f"Loaded and cleaned {len(cleaned_documents)} pages")

        # Show preview of first page
        if cleaned_documents:
            preview = cleaned_documents[0].page_content[:300]
            logger.info(f"First page preview:\n{preview}...")
    else:
        logger.warning(f"PDF file not found: {local_pdf}")

    # Example 2: Load hybrid PDF (handles both scanned and text-based pages automatically)
    logger.info("\n" + "=" * 50)
    logger.info("Example 2: Using Hybrid Loader for mixed PDFs")
    logger.info("=" * 50)

    if local_pdf.exists():
        logger.info(f"Loading hybrid PDF from: {local_pdf}")
        # Hybrid loader automatically detects each page and uses appropriate method
        hybrid_documents = hybrid_loader.load_from_local(str(local_pdf))
        cleaned_hybrid = text_cleaner.clean_documents(hybrid_documents)
        logger.info(
            f"Loaded and cleaned {len(cleaned_hybrid)} pages using hybrid loader"
        )

    # Example 3: Load from URL (commented out - uncomment to test)
    # url = "https://example.com/document.pdf"
    # logger.info(f"Downloading and loading PDF from URL: {url}")
    # documents = hybrid_loader.load_from_url(url)  # Use hybrid loader for unknown PDFs
    # cleaned_documents = text_cleaner.clean_documents(documents)
    # logger.info(f"Loaded and cleaned {len(cleaned_documents)} pages from URL")

    # Example 4: Scrape text from a single web page
    logger.info("\n" + "=" * 50)
    logger.info("Example 4: Scraping text from web pages")
    logger.info("=" * 50)

    # Example URL from sites.txt
    example_url = "https://ghanalawhub.com/summary-transparency-international-ors-v-republic-of-ghana-the-agyapa-case/"
    logger.info(f"Scraping web page: {example_url}")

    try:
        web_document = web_scraper.scrape_url(example_url)
        if web_document:
            # Clean the web document
            cleaned_web = text_cleaner.clean_document(web_document)

            logger.info(f"Title: {cleaned_web.metadata.get('title', 'N/A')}")
            logger.info(f"Scraped {len(cleaned_web.page_content)} characters")

            # Show preview
            preview = cleaned_web.page_content[:500].replace("\n", " ")
            logger.info(f"Content preview:\n{preview}...")
        else:
            logger.warning(f"Failed to scrape {example_url}")
    except Exception as e:
        logger.error(f"Error scraping web page: {e}")

    # Example 5: Scrape multiple URLs from sites.txt file
    logger.info("\n" + "=" * 50)
    logger.info("Example 5: Scraping multiple URLs from sites.txt")
    logger.info("=" * 50)

    sites_file = Path(__file__).parent.parent / "data" / "sites.txt"
    if sites_file.exists():
        logger.info(f"Scraping URLs from: {sites_file}")
        try:
            web_documents = web_scraper.scrape_from_file(str(sites_file))
            if web_documents:
                # Clean all web documents
                cleaned_web_docs = text_cleaner.clean_documents(web_documents)

                logger.info(
                    f"Successfully scraped and cleaned {len(cleaned_web_docs)} web pages"
                )

                # Show summary
                for i, doc in enumerate(cleaned_web_docs[:3], 1):
                    title = doc.metadata.get("title", "N/A")
                    url = doc.metadata.get("url", "N/A")
                    length = len(doc.page_content)
                    logger.info(f"  {i}. {title[:60]}... ({length} chars)")
                    logger.info(f"     URL: {url}")

                if len(cleaned_web_docs) > 3:
                    logger.info(f"  ... and {len(cleaned_web_docs) - 3} more pages")
            else:
                logger.warning("No documents were successfully scraped")
        except Exception as e:
            logger.error(f"Error scraping from file: {e}")
    else:
        logger.warning(f"Sites file not found: {sites_file}")

    # Example 6: Scrape multiple URLs programmatically
    logger.info("\n" + "=" * 50)
    logger.info("Example 6: Scraping multiple URLs programmatically")
    logger.info("=" * 50)

    example_urls = [
        "https://judicial.gov.gh/index.php/supreme-court-judges",
        "https://judicial.gov.gh/index.php/court-of-appeal-judges",
    ]

    logger.info(f"Scraping {len(example_urls)} URLs...")
    try:
        web_docs = web_scraper.scrape_urls(example_urls)
        if web_docs:
            cleaned_web_docs = text_cleaner.clean_documents(web_docs)
            logger.info(
                f"Successfully scraped and cleaned {len(cleaned_web_docs)} web pages"
            )

            for doc in cleaned_web_docs:
                title = doc.metadata.get("title", "N/A")
                logger.info(f"  - {title}")
        else:
            logger.warning("No documents were successfully scraped")
    except Exception as e:
        logger.error(f"Error scraping URLs: {e}")


if __name__ == "__main__":
    main()
