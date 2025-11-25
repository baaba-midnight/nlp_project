"""
Hybrid PDF Loader Service
Handles PDFs that contain both scanned and text-based pages.
Automatically detects each page and uses the appropriate extraction method.
"""

import os
import logging
from typing import List, Optional

from langchain_core.documents import Document

from app.services.pdf_loader import PDFLoaderService
from app.services.ocr_loader import OCRLoaderService

logger = logging.getLogger(__name__)


class HybridPDFLoader:
    """Service for loading hybrid PDFs with mixed scanned and text-based pages."""
    
    def __init__(
        self, 
        pdf_loader: Optional[PDFLoaderService] = None,
        ocr_loader: Optional[OCRLoaderService] = None,
        page_threshold: int = 100
    ):
        """
        Initialize Hybrid PDF Loader.
        
        Args:
            pdf_loader: PDFLoaderService instance (creates new if None)
            ocr_loader: OCRLoaderService instance (creates new if None)
            page_threshold: Minimum characters to consider page as text-based (default: 100)
        """
        self.pdf_loader = pdf_loader or PDFLoaderService()
        self.ocr_loader = ocr_loader or OCRLoaderService()
        self.page_threshold = page_threshold
    
    def load_pdf(self, pdf_path: str, dpi: int = 300, lang: str = 'eng') -> List[Document]:
        """
        Load PDF with automatic detection and extraction per page.
        
        For each page:
        - If page has sufficient text (>= threshold chars), use PyPDF extraction
        - If page has insufficient text (< threshold chars), use OCR extraction
        
        Args:
            pdf_path: Path to PDF file
            dpi: Resolution for OCR image conversion (default: 300)
            lang: Language code for OCR (default: 'eng')
            
        Returns:
            List of Document objects with extracted text and metadata
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        logger.info(f"Loading hybrid PDF: {pdf_path}")
        
        # Get total number of pages
        import pypdf
        with open(pdf_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            total_pages = len(pdf_reader.pages)
        
        documents = []
        scanned_count = 0
        text_based_count = 0
        
        for page_num in range(total_pages):
            # Check if page is scanned
            is_scanned = self.pdf_loader.is_page_scanned(
                pdf_path, 
                page_num, 
                threshold=self.page_threshold
            )
            
            if is_scanned:
                # Use OCR for scanned pages
                logger.debug(f"Page {page_num + 1}: Using OCR (scanned)")
                doc = self.ocr_loader.load_page(pdf_path, page_num, dpi=dpi, lang=lang)
                scanned_count += 1
            else:
                # Use PyPDF for text-based pages
                logger.debug(f"Page {page_num + 1}: Using PyPDF (text-based)")
                doc = self.pdf_loader.load_page(pdf_path, page_num)
                text_based_count += 1
            
            if doc:
                documents.append(doc)
            else:
                logger.warning(f"Failed to extract page {page_num + 1}, skipping")
        
        logger.info(
            f"Hybrid PDF loaded: {len(documents)} pages total "
            f"({text_based_count} text-based, {scanned_count} scanned)"
        )
        
        return documents
    
    def load_from_url(self, url: str, dpi: int = 300, lang: str = 'eng') -> List[Document]:
        """
        Download PDF from URL and load it as hybrid PDF.
        
        Args:
            url: URL of the PDF
            dpi: Resolution for OCR image conversion (default: 300)
            lang: Language code for OCR (default: 'eng')
            
        Returns:
            List of Document objects
        """
        local_path = self.pdf_loader.fetch_from_url(url)
        return self.load_pdf(local_path, dpi=dpi, lang=lang)
    
    def load_from_local(self, pdf_path: str, dpi: int = 300, lang: str = 'eng') -> List[Document]:
        """
        Load hybrid PDF from local path.
        
        Args:
            pdf_path: Local path to PDF file
            dpi: Resolution for OCR image conversion (default: 300)
            lang: Language code for OCR (default: 'eng')
            
        Returns:
            List of Document objects
        """
        return self.load_pdf(pdf_path, dpi=dpi, lang=lang)

