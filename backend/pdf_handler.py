"""
PDF Handler
Manages PDF file operations: fetch, cache, and validation
"""

import os
import tempfile
import logging
from pathlib import Path
from typing import Optional, Tuple
from lark_client import get_lark_client

logger = logging.getLogger(__name__)

class PDFHandler:
    """Handle PDF file operations with caching"""
    
    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = Path(cache_dir or tempfile.gettempdir()) / "lark_pdf_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"PDF cache directory: {self.cache_dir}")
    
    def get_cache_path(self, file_id: str) -> Path:
        """Get the cache file path for a given file ID"""
        return self.cache_dir / f"{file_id}.pdf"
    
    def is_cached(self, file_id: str) -> bool:
        """Check if PDF is cached locally"""
        cache_path = self.get_cache_path(file_id)
        return cache_path.exists()
    
    def fetch_pdf(self, file_id: str, force_refresh: bool = False) -> Tuple[bytes, Path]:
        """
        Fetch PDF from Lark or use cached version
        
        Args:
            file_id: The Lark file ID
            force_refresh: Force download even if cached
        
        Returns:
            Tuple of (file_content_bytes, cache_file_path)
        """
        cache_path = self.get_cache_path(file_id)
        
        # Return cached version if available
        if not force_refresh and self.is_cached(file_id):
            logger.info(f"Using cached PDF: {file_id}")
            with open(cache_path, 'rb') as f:
                return f.read(), cache_path
        
        # Download from Lark
        logger.info(f"Downloading PDF from Lark: {file_id}")
        lark_client = get_lark_client()
        
        try:
            pdf_content = lark_client.get_file(file_id)
            
            # Validate it's a PDF
            if not pdf_content.startswith(b'%PDF'):
                raise ValueError(f"File {file_id} is not a valid PDF")
            
            # Cache it
            with open(cache_path, 'wb') as f:
                f.write(pdf_content)
            
            logger.info(f"PDF cached: {file_id} ({len(pdf_content)} bytes)")
            return pdf_content, cache_path
            
        except Exception as e:
            logger.error(f"Failed to fetch PDF {file_id}: {e}")
            raise
    
    def validate_pdf(self, pdf_content: bytes) -> bool:
        """
        Validate that content is a valid PDF
        
        Args:
            pdf_content: PDF file content as bytes
        
        Returns:
            True if valid PDF
        """
        if not pdf_content:
            return False
        
        # Check PDF magic bytes
        if not pdf_content.startswith(b'%PDF'):
            return False
        
        # Check for PDF end marker
        if b'%%EOF' not in pdf_content:
            return False
        
        return True
    
    def clear_cache(self, file_id: Optional[str] = None):
        """
        Clear cached PDFs
        
        Args:
            file_id: Clear specific file, or None to clear all
        """
        if file_id:
            cache_path = self.get_cache_path(file_id)
            if cache_path.exists():
                cache_path.unlink()
                logger.info(f"Cleared cache for {file_id}")
        else:
            import shutil
            if self.cache_dir.exists():
                shutil.rmtree(self.cache_dir)
                self.cache_dir.mkdir(parents=True, exist_ok=True)
                logger.info("Cleared all PDF cache")


# Global handler instance
_pdf_handler = None

def get_pdf_handler() -> PDFHandler:
    """Get or create the PDF handler singleton"""
    global _pdf_handler
    if _pdf_handler is None:
        _pdf_handler = PDFHandler()
    return _pdf_handler
