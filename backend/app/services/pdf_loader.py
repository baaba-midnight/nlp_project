"""
PDF Loader Service
Handles fetching/downloading PDFs from URLs or local paths,
detects scanned vs native PDFs, and extracts text using PyPDF.
"""

import os
import urllib.request
import urllib.parse
from pathlib import Path
from typing import List, Optional, Union
import logging

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
import pypdf

logger = logging.getLogger(__name__)


class PDFLoaderService:
    """Service for loading and processing PDF documents."""
    
    def __init__(self, download_dir: Optional[str] = None):
        """
        Initialize PDF Loader Service.
        
        Args:
            download_dir: Directory to save downloaded PDFs (default: ./downloads)
        """
        self.download_dir = download_dir or os.path.join(os.getcwd(), "downloads")
        os.makedirs(self.download_dir, exist_ok=True)
    
    def fetch_from_url(self, url: str, filename: Optional[str] = None) -> str:
        """
        Download PDF from URL.
        
        Args:
            url: URL of the PDF to download
            filename: Optional custom filename (default: extracted from URL)
            
        Returns:
            Local file path to the downloaded PDF
        """
        try:
            if not filename:
                # Extract filename from URL
                parsed_url = urllib.parse.urlparse(url)
                filename = os.path.basename(parsed_url.path) or "downloaded.pdf"
            
            filepath = os.path.join(self.download_dir, filename)
            
            logger.info(f"Downloading PDF from {url} to {filepath}")
            urllib.request.urlretrieve(url, filepath)
            logger.info(f"Successfully downloaded PDF to {filepath}")
            
            return filepath
        except Exception as e:
            logger.error(f"Error downloading PDF from {url}: {str(e)}")
            raise
    
    def is_page_scanned(self, pdf_path: str, page_num: int, threshold: int = 100) -> bool:
        """
        Detect if a specific page in a PDF is scanned (image-based) or native (text-based).
        
        Args:
            pdf_path: Path to PDF file
            page_num: Zero-indexed page number to check
            threshold: Minimum characters to consider page as text-based (default: 100)
            
        Returns:
            True if page appears to be scanned, False if native
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                if page_num >= len(pdf_reader.pages):
                    logger.warning(f"Page {page_num} out of range, assuming scanned")
                    return True
                
                try:
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    text_length = len(text.strip())
                    
                    is_scanned = text_length < threshold
                    return is_scanned
                except Exception as e:
                    logger.warning(f"Error extracting text from page {page_num}: {e}")
                    return True  # On error, assume scanned
                    
        except Exception as e:
            logger.error(f"Error detecting page type: {str(e)}")
            return True  # On error, assume scanned
    
    def is_scanned_pdf(self, pdf_path: str, sample_pages: int = 3) -> bool:
        """
        Detect if PDF is scanned (image-based) or native (text-based).
        
        Strategy:
        1. Try to extract text from sample pages
        2. If text extraction yields very little text, likely scanned
        3. Check if PDF has text layers
        
        Args:
            pdf_path: Path to PDF file
            sample_pages: Number of pages to sample for detection (default: 3)
            
        Returns:
            True if PDF appears to be scanned, False if native
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                # Sample pages (first, middle, last)
                pages_to_check = []
                if total_pages == 0:
                    return True  # Empty PDF, assume scanned
                
                if total_pages == 1:
                    pages_to_check = [0]
                else:
                    pages_to_check = [0]  # First page
                    if total_pages > 2:
                        pages_to_check.append(total_pages // 2)  # Middle page
                    pages_to_check.append(total_pages - 1)  # Last page
                
                total_text_length = 0
                
                for page_num in pages_to_check[:sample_pages]:
                    try:
                        page = pdf_reader.pages[page_num]
                        text = page.extract_text()
                        total_text_length += len(text.strip())
                    except Exception as e:
                        logger.warning(f"Error extracting text from page {page_num}: {e}")
                        continue
                
                # Threshold: if average text per page is less than 100 chars, likely scanned
                avg_text_per_page = total_text_length / len(pages_to_check) if pages_to_check else 0
                
                is_scanned = avg_text_per_page < 100
                
                logger.info(
                    f"PDF detection for {pdf_path}: "
                    f"avg_text={avg_text_per_page:.0f} chars/page, "
                    f"is_scanned={is_scanned}"
                )
                
                return is_scanned
                
        except Exception as e:
            logger.error(f"Error detecting PDF type for {pdf_path}: {str(e)}")
            # On error, assume it's scanned to be safe (will trigger OCR)
            return True
    
    def load_pdf(
        self, 
        pdf_path: str, 
        is_scanned: Optional[bool] = None
    ) -> List[Document]:
        """
        Load PDF and extract text using PyPDFLoader.
        
        Args:
            pdf_path: Path to PDF file (local)
            is_scanned: Optional pre-determined scan status (if None, will auto-detect)
            
        Returns:
            List of Document objects with text and metadata
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Auto-detect if not provided
        if is_scanned is None:
            is_scanned = self.is_scanned_pdf(pdf_path)
        
        if is_scanned:
            logger.warning(
                f"PDF {pdf_path} appears to be scanned. "
                f"Consider using OCRLoaderService for better extraction."
            )
        
        try:
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            
            # Add metadata about PDF type
            for doc in documents:
                doc.metadata['is_scanned'] = is_scanned
                doc.metadata['pdf_source'] = pdf_path
                doc.metadata['pdf_filename'] = os.path.basename(pdf_path)
            
            logger.info(f"Successfully loaded {len(documents)} pages from {pdf_path}")
            return documents
            
        except Exception as e:
            logger.error(f"Error loading PDF {pdf_path}: {str(e)}")
            raise
    
    def load_from_url(self, url: str) -> List[Document]:
        """
        Download PDF from URL and load it.
        
        Args:
            url: URL of the PDF
            
        Returns:
            List of Document objects
        """
        local_path = self.fetch_from_url(url)
        return self.load_pdf(local_path)
    
    def load_from_local(self, pdf_path: str) -> List[Document]:
        """
        Load PDF from local path.
        
        Args:
            pdf_path: Local path to PDF file
            
        Returns:
            List of Document objects
        """
        return self.load_pdf(pdf_path)
    
    def load_page(self, pdf_path: str, page_num: int) -> Optional[Document]:
        """
        Load a single page from PDF using PyPDF.
        
        Args:
            pdf_path: Path to PDF file
            page_num: Zero-indexed page number
            
        Returns:
            Document object for the page, or None if error
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                if page_num >= len(pdf_reader.pages):
                    logger.warning(f"Page {page_num} out of range")
                    return None
                
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                
                doc = Document(
                    page_content=text,
                    metadata={
                        'source': pdf_path,
                        'page': page_num + 1,
                        'pdf_source': pdf_path,
                        'pdf_filename': os.path.basename(pdf_path),
                        'is_scanned': False,
                        'extraction_method': 'PyPDF'
                    }
                )
                return doc
        except Exception as e:
            logger.error(f"Error loading page {page_num} from {pdf_path}: {str(e)}")
            return None

