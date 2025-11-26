"""
OCR Loader Service
Handles OCR extraction from scanned PDFs using pytesseract.
"""

import os
import logging
from typing import List, Optional
from pathlib import Path

import pytesseract
from PIL import Image
import fitz  # PyMuPDF
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class OCRLoaderService:
    """Service for OCR extraction from scanned PDFs."""
    
    def __init__(self, tesseract_cmd: Optional[str] = None):
        """
        Initialize OCR Loader Service.
        
        Args:
            tesseract_cmd: Path to tesseract executable (if not in PATH)
                          On Windows, might be: r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        
        # Verify tesseract is available
        try:
            pytesseract.get_tesseract_version()
            logger.info("Tesseract OCR initialized successfully")
        except Exception as e:
            logger.warning(f"Tesseract OCR may not be properly installed: {e}")
            logger.warning("Please install Tesseract OCR: https://github.com/tesseract-ocr/tesseract")
    
    def pdf_to_images(self, pdf_path: str, dpi: int = 300) -> List[Image.Image]:
        """
        Convert PDF pages to PIL Images.
        
        Args:
            pdf_path: Path to PDF file
            dpi: Resolution for image conversion (default: 300)
            
        Returns:
            List of PIL Image objects, one per page
        """
        try:
            pdf_document = fitz.open(pdf_path)
            images = []
            
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                # Convert page to image
                mat = fitz.Matrix(dpi / 72, dpi / 72)  # 72 is default DPI
                pix = page.get_pixmap(matrix=mat)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                images.append(img)
            
            pdf_document.close()
            logger.info(f"Converted {len(images)} pages from PDF to images")
            return images
            
        except Exception as e:
            logger.error(f"Error converting PDF to images: {str(e)}")
            raise
    
    def extract_text_from_image(self, image: Image.Image, lang: str = 'eng') -> str:
        """
        Extract text from a single image using OCR.
        
        Args:
            image: PIL Image object
            lang: Language code for OCR (default: 'eng')
            
        Returns:
            Extracted text string
        """
        try:
            text = pytesseract.image_to_string(image, lang=lang)
            return text
        except Exception as e:
            logger.error(f"Error extracting text from image: {str(e)}")
            raise
    
    def load_page(self, pdf_path: str, page_num: int, dpi: int = 300, lang: str = 'eng') -> Optional[Document]:
        """
        Load a single page from PDF using OCR.
        
        Args:
            pdf_path: Path to PDF file
            page_num: Zero-indexed page number
            dpi: Resolution for image conversion (default: 300)
            lang: Language code for OCR (default: 'eng')
            
        Returns:
            Document object for the page, or None if error
        """
        try:
            pdf_document = fitz.open(pdf_path)
            if page_num >= len(pdf_document):
                logger.warning(f"Page {page_num} out of range")
                pdf_document.close()
                return None
            
            page = pdf_document[page_num]
            # Convert page to image
            mat = fitz.Matrix(dpi / 72, dpi / 72)
            pix = page.get_pixmap(matrix=mat)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            pdf_document.close()
            
            # Extract text from image
            text = self.extract_text_from_image(img, lang=lang)
            
            doc = Document(
                page_content=text,
                metadata={
                    'source': pdf_path,
                    'page': page_num + 1,
                    'pdf_source': pdf_path,
                    'pdf_filename': os.path.basename(pdf_path),
                    'is_scanned': True,
                    'extraction_method': 'OCR',
                    'dpi': dpi,
                    'ocr_lang': lang
                }
            )
            return doc
        except Exception as e:
            logger.error(f"Error loading page {page_num} with OCR: {str(e)}")
            return None
    
    def load_pdf(
        self, 
        pdf_path: str, 
        dpi: int = 300,
        lang: str = 'eng'
    ) -> List[Document]:
        """
        Load scanned PDF and extract text using OCR.
        
        Args:
            pdf_path: Path to PDF file
            dpi: Resolution for image conversion (default: 300)
            lang: Language code for OCR (default: 'eng')
            
        Returns:
            List of Document objects with extracted text and metadata
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        logger.info(f"Starting OCR extraction from {pdf_path}")
        
        try:
            # Convert PDF to images
            images = self.pdf_to_images(pdf_path, dpi=dpi)
            
            documents = []
            
            for page_num, image in enumerate(images):
                # Extract text from image
                text = self.extract_text_from_image(image, lang=lang)
                
                # Create Document object
                doc = Document(
                    page_content=text,
                    metadata={
                        'source': pdf_path,
                        'page': page_num + 1,
                        'pdf_source': pdf_path,
                        'pdf_filename': os.path.basename(pdf_path),
                        'is_scanned': True,
                        'extraction_method': 'OCR',
                        'dpi': dpi,
                        'ocr_lang': lang
                    }
                )
                documents.append(doc)
            
            logger.info(f"Successfully extracted text from {len(documents)} pages using OCR")
            return documents
            
        except Exception as e:
            logger.error(f"Error loading PDF with OCR: {str(e)}")
            raise

