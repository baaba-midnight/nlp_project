"""
Text Cleaner Utility
Removes headers, footers, page numbers, and other unwanted text patterns.
"""

import re
import logging
from typing import List, Optional

from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class TextCleaner:
    """Utility for cleaning extracted text from PDFs."""
    
    def __init__(self):
        """Initialize Text Cleaner with common patterns."""
        # Common patterns to remove
        self.page_number_patterns = [
            r'\bPage\s+\d+\b',  # "Page 1", "Page 2", etc.
            r'\b\d+\s+of\s+\d+\b',  # "1 of 10", "2 of 10", etc.
            r'^\d+$',  # Standalone page numbers
            r'^-\s*\d+\s*-$',  # "- 1 -", "- 2 -"
            r'^\d+\s*/\s*\d+$',  # "1/10", "2/10"
        ]
        
        # Common header/footer patterns (often repeated across pages)
        self.header_footer_patterns = [
            r'^.*?Government of Ghana.*?$',
            r'^.*?Parliament of Ghana.*?$',
            r'^.*?Ministry of.*?$',
            r'^.*?©.*?$',  # Copyright notices
            r'^.*?Confidential.*?$',
            r'^.*?DRAFT.*?$',
        ]
        
        # Watermark patterns
        self.watermark_patterns = [
            r'CONFIDENTIAL',
            r'DRAFT',
            r'NOT FOR DISTRIBUTION',
        ]
    
    def remove_page_numbers(self, text: str) -> str:
        """
        Remove page numbers from text.
        
        Args:
            text: Input text
            
        Returns:
            Cleaned text without page numbers
        """
        cleaned = text
        
        for pattern in self.page_number_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.MULTILINE | re.IGNORECASE)
        
        return cleaned
    
    def remove_headers_footers(self, text: str, min_repetition: int = 2) -> str:
        """
        Remove headers and footers that appear repeatedly.
        
        Strategy: Find lines that appear at the start/end of multiple pages.
        
        Args:
            text: Input text
            min_repetition: Minimum times a line must appear to be considered header/footer
            
        Returns:
            Cleaned text without headers/footers
        """
        lines = text.split('\n')
        cleaned_lines = []
        
        # Track line frequencies
        line_counts = {}
        for line in lines:
            stripped = line.strip()
            if stripped:
                line_counts[stripped] = line_counts.get(stripped, 0) + 1
        
        # Remove lines that appear too frequently (likely headers/footers)
        for line in lines:
            stripped = line.strip()
            if stripped and line_counts.get(stripped, 0) >= min_repetition:
                # Check if it matches header/footer patterns
                is_header_footer = any(
                    re.match(pattern, stripped, re.IGNORECASE)
                    for pattern in self.header_footer_patterns
                )
                if is_header_footer:
                    continue  # Skip this line
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def remove_watermarks(self, text: str) -> str:
        """
        Remove watermark text.
        
        Args:
            text: Input text
            
        Returns:
            Cleaned text without watermarks
        """
        cleaned = text
        
        for pattern in self.watermark_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        return cleaned
    
    def remove_extra_whitespace(self, text: str) -> str:
        """
        Remove excessive whitespace and normalize.
        
        Args:
            text: Input text
            
        Returns:
            Text with normalized whitespace
        """
        # Replace multiple spaces with single space
        cleaned = re.sub(r' +', ' ', text)
        # Replace multiple newlines with max 2 newlines
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in cleaned.split('\n')]
        # Remove empty lines at start and end
        while lines and not lines[0]:
            lines.pop(0)
        while lines and not lines[-1]:
            lines.pop()
        
        return '\n'.join(lines)
    
    def clean_text(self, text: str, remove_headers: bool = True) -> str:
        """
        Apply all cleaning operations to text.
        
        Args:
            text: Input text to clean
            remove_headers: Whether to remove headers/footers (default: True)
            
        Returns:
            Fully cleaned text
        """
        cleaned = text
        
        # Remove watermarks first
        cleaned = self.remove_watermarks(cleaned)
        
        # Remove page numbers
        cleaned = self.remove_page_numbers(cleaned)
        
        # Remove headers/footers if requested
        if remove_headers:
            cleaned = self.remove_headers_footers(cleaned)
        
        # Normalize whitespace
        cleaned = self.remove_extra_whitespace(cleaned)
        
        return cleaned
    
    def clean_document(self, document: Document, remove_headers: bool = True) -> Document:
        """
        Clean a single Document object.
        
        Args:
            document: LangChain Document object
            remove_headers: Whether to remove headers/footers (default: True)
            
        Returns:
            Document with cleaned text
        """
        cleaned_text = self.clean_text(document.page_content, remove_headers=remove_headers)
        
        # Create new document with cleaned text and same metadata
        return Document(
            page_content=cleaned_text,
            metadata=document.metadata
        )
    
    def clean_documents(
        self, 
        documents: List[Document], 
        remove_headers: bool = True
    ) -> List[Document]:
        """
        Clean a list of Document objects.
        
        Args:
            documents: List of LangChain Document objects
            remove_headers: Whether to remove headers/footers (default: True)
            
        Returns:
            List of Documents with cleaned text
        """
        cleaned_docs = []
        
        for doc in documents:
            try:
                cleaned_doc = self.clean_document(doc, remove_headers=remove_headers)
                cleaned_docs.append(cleaned_doc)
            except Exception as e:
                logger.warning(f"Error cleaning document: {e}. Keeping original.")
                cleaned_docs.append(doc)
        
        logger.info(f"Cleaned {len(cleaned_docs)} documents")
        return cleaned_docs

