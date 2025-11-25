"""
File: ingestion.py
Project: services
File Created: Tuesday, 18th November 2025 8:27:29 PM
Author: baaba-midnight
Email: baaba.amosah@gmail.com
Version: 1.0
Brief: Service for ingesting and processing documents into the vector store. 
-----
Last Modified: Tuesday, 18th November 2025 9:24:45 PM
Modified By: baaba-midnight
-----
Copyright ©2025 baaba-midnight
"""
from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass
class Document:
    """Document model representing a text document to be ingested."""
    source: str
    text: str
    title: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

@dataclass
class Chunk:
    """Chunk model representing a chunked segment of a document."""
    text: str
    start: int
    end: int
    metadata: Dict = field(default_factory=dict)