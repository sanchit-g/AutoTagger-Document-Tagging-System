"""
File handling utilities for document upload and text extraction
"""
import os
import logging
from pathlib import Path
from typing import Optional, Tuple

import PyPDF2
import pdfplumber

logger = logging.getLogger(__name__)

class FileHandler:
    """Handle file operations and text extraction"""
    
    def __init__(self, upload_folder: str, allowed_extensions: set):
        """
        Initialize file handler
        
        Args:
            upload_folder: Directory to store uploaded files
            allowed_extensions: Set of allowed file extensions
        """
        self.upload_folder = Path(upload_folder)
        self.allowed_extensions = allowed_extensions
        
        # Ensure upload folder exists
        self.upload_folder.mkdir(parents=True, exist_ok=True)
    
    def allowed_file(self, filename: str) -> bool:
        """
        Check if file has allowed extension
        
        Args:
            filename: Name of the file
            
        Returns:
            True if file is allowed, False otherwise
        """
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def save_file(self, file, filename: str) -> Tuple[bool, str, Optional[Path]]:
        """
        Save uploaded file
        
        Args:
            file: File object from Flask request
            filename: Original filename
            
        Returns:
            Tuple of (success, message, filepath)
        """
        try:
            if not self.allowed_file(filename):
                return False, f"File type not allowed. Allowed types: {', '.join(self.allowed_extensions)}", None
            
            # Generate unique filename if file already exists
            filepath = self.upload_folder / filename
            counter = 1
            while filepath.exists():
                name, ext = os.path.splitext(filename)
                filepath = self.upload_folder / f"{name}_{counter}{ext}"
                counter += 1
            
            # Save file
            file.save(str(filepath))
            logger.info(f"File saved: {filepath}")
            
            return True, "File saved successfully", filepath
            
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            return False, f"Error saving file: {str(e)}", None
    
    def extract_text_from_txt(self, filepath: Path) -> Tuple[bool, str, Optional[str]]:
        """
        Extract text from TXT file
        
        Args:
            filepath: Path to TXT file
            
        Returns:
            Tuple of (success, message, content)
        """
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if not content.strip():
                return False, "File is empty", None
            
            logger.info(f"Extracted {len(content)} characters from TXT file")
            return True, "Text extracted successfully", content
            
        except Exception as e:
            logger.error(f"Error reading TXT file: {e}")
            return False, f"Error reading TXT file: {str(e)}", None
    
    def extract_text_from_pdf(self, filepath: Path) -> Tuple[bool, str, Optional[str]]:
        """
        Extract text from PDF file using multiple methods
        
        Args:
            filepath: Path to PDF file
            
        Returns:
            Tuple of (success, message, content)
        """
        # Try pdfplumber first (better for complex PDFs)
        content = self._extract_with_pdfplumber(filepath)
        
        # If pdfplumber fails, try PyPDF2
        if not content:
            content = self._extract_with_pypdf2(filepath)
        
        if not content:
            return False, "Could not extract text from PDF. File may be scanned or corrupted.", None
        
        logger.info(f"Extracted {len(content)} characters from PDF file")
        return True, "Text extracted successfully", content
    
    def _extract_with_pdfplumber(self, filepath: Path) -> Optional[str]:
        """Extract text using pdfplumber"""
        try:
            text_parts = []
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
            
            content = '\n'.join(text_parts)
            return content if content.strip() else None
            
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {e}")
            return None
    
    def _extract_with_pypdf2(self, filepath: Path) -> Optional[str]:
        """Extract text using PyPDF2"""
        try:
            text_parts = []
            with open(filepath, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
            
            content = '\n'.join(text_parts)
            return content if content.strip() else None
            
        except Exception as e:
            logger.warning(f"PyPDF2 extraction failed: {e}")
            return None
    
    def extract_text(self, filepath: Path) -> Tuple[bool, str, Optional[str]]:
        """
        Extract text from file based on extension
        
        Args:
            filepath: Path to file
            
        Returns:
            Tuple of (success, message, content)
        """
        extension = filepath.suffix.lower()
        
        if extension == '.txt':
            return self.extract_text_from_txt(filepath)
        elif extension == '.pdf':
            return self.extract_text_from_pdf(filepath)
        else:
            return False, f"Unsupported file type: {extension}", None
    
    def delete_file(self, filepath: Path) -> bool:
        """
        Delete a file
        
        Args:
            filepath: Path to file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if filepath.exists():
                filepath.unlink()
                logger.info(f"Deleted file: {filepath}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False