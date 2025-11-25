"""
Test script for preprocessing services.

Run this from the backend directory:
    python test_preprocessing.py
"""

import sys
from pathlib import Path

# Ensure we can import app modules
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import logging
from app.services.pdf_loader import PDFLoaderService
from app.services.ocr_loader import OCRLoaderService
from app.services.hybrid_loader import HybridPDFLoader
from app.utils.text_cleaner import TextCleaner

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Test the preprocessing services."""
    
    # Initialize services
    pdf_loader = PDFLoaderService()
    ocr_loader = OCRLoaderService()
    hybrid_loader = HybridPDFLoader()
    text_cleaner = TextCleaner()
    
    # Find a PDF in the data directory
    data_dir = Path(__file__).parent / "app" / "data"
    pdf_files = list(data_dir.glob("*.pdf"))
    
    if not pdf_files:
        logger.error(f"No PDF files found in {data_dir}")
        return
    
    # Use the first PDF found
    test_pdf = pdf_files[0]
    logger.info(f"Testing with PDF: {test_pdf.name}")
    logger.info("=" * 60)
    
    # Test 1: Check if PDF is scanned
    logger.info("\n1. Checking if PDF is scanned...")
    is_scanned = pdf_loader.is_scanned_pdf(str(test_pdf))
    logger.info(f"   Result: {'Scanned' if is_scanned else 'Text-based'}")
    
    # Test 2: Load with hybrid loader (handles both types)
    logger.info("\n2. Loading PDF with hybrid loader...")
    try:
        documents = hybrid_loader.load_from_local(str(test_pdf))
        logger.info(f"   Successfully loaded {len(documents)} pages")
        
        # Show extraction method for first few pages
        for i, doc in enumerate(documents[:3]):
            method = doc.metadata.get('extraction_method', 'Unknown')
            page_num = doc.metadata.get('page', i + 1)
            logger.info(f"   Page {page_num}: {method}")
        
        if len(documents) > 3:
            logger.info(f"   ... and {len(documents) - 3} more pages")
    
    except Exception as e:
        logger.error(f"   Error loading PDF: {e}")
        return
    
    # Test 3: Clean documents
    logger.info("\n3. Cleaning documents...")
    try:
        cleaned_docs = text_cleaner.clean_documents(documents)
        logger.info(f"   Successfully cleaned {len(cleaned_docs)} documents")
        
        # Show preview of first page
        if cleaned_docs:
            preview = cleaned_docs[0].page_content[:200].replace('\n', ' ')
            logger.info(f"   First page preview: {preview}...")
    
    except Exception as e:
        logger.error(f"   Error cleaning documents: {e}")
    
    logger.info("\n" + "=" * 60)
    logger.info("Test completed!")


if __name__ == "__main__":
    main()

