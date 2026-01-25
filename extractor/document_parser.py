"""
Document Parser Module

High-level interface for document extraction.
Handles preprocessing, extraction, and post-processing.
"""

import os
from typing import Optional, Dict, Any, List
from pathlib import Path
import tempfile

from extractor.vision_ai import VisionAI
from utils.image_utils import preprocess_image, pdf_to_images


class DocumentExtractor:
    """
    High-level document data extractor.
    
    Provides a simple interface for extracting structured data
    from various document types (PDF, images).
    
    Example:
        extractor = DocumentExtractor()
        data = extractor.extract("invoice.pdf")
        print(data['total_amount'])
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the document extractor.
        
        Args:
            api_key: OpenAI API key (optional, uses env var if not provided)
        """
        self.vision_ai = VisionAI(api_key=api_key)
        self.supported_images = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
        self.supported_pdfs = {'.pdf'}
    
    def extract(
        self, 
        file_path: str, 
        document_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract structured data from a document.
        
        Handles both PDFs and images. For PDFs, converts to image first.
        
        Args:
            file_path: Path to the document file
            document_type: Optional document type hint
            
        Returns:
            Dictionary containing extracted data
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        extension = path.suffix.lower()
        
        # Handle PDF documents
        if extension in self.supported_pdfs:
            return self._extract_from_pdf(file_path, document_type)
        
        # Handle image documents
        elif extension in self.supported_images:
            return self._extract_from_image(file_path, document_type)
        
        else:
            raise ValueError(f"Unsupported file type: {extension}")
    
    def _extract_from_image(
        self, 
        image_path: str, 
        document_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract data from an image document.
        
        Args:
            image_path: Path to the image file
            document_type: Optional document type hint
            
        Returns:
            Extracted data dictionary
        """
        # Preprocess the image for better OCR
        processed_path = preprocess_image(image_path)
        
        try:
            # Use preprocessed image if available, otherwise original
            path_to_use = processed_path or image_path
            
            # Determine document type
            doc_type = document_type or 'auto'
            
            # Extract data using Vision AI
            data = self.vision_ai.analyze_document(path_to_use, doc_type)
            
            return data
            
        finally:
            # Clean up temporary preprocessed file
            if processed_path and processed_path != image_path:
                try:
                    os.unlink(processed_path)
                except Exception:
                    pass
    
    def _extract_from_pdf(
        self, 
        pdf_path: str, 
        document_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract data from a PDF document.
        
        Converts PDF to image(s) and processes the first page.
        For multi-page PDFs, only the first page is processed by default.
        
        Args:
            pdf_path: Path to the PDF file
            document_type: Optional document type hint
            
        Returns:
            Extracted data dictionary
        """
        # Convert PDF to images
        images = pdf_to_images(pdf_path)
        
        if not images:
            raise ValueError("Failed to convert PDF to images")
        
        try:
            # Process the first page
            # For multi-page documents, you could extend this to process all pages
            first_page = images[0]
            
            return self._extract_from_image(first_page, document_type)
            
        finally:
            # Clean up temporary image files
            for img_path in images:
                try:
                    os.unlink(img_path)
                except Exception:
                    pass
    
    def batch_extract(
        self, 
        directory: str, 
        document_type: Optional[str] = None,
        output_excel: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract data from multiple documents in a directory.
        
        Args:
            directory: Path to directory containing documents
            document_type: Optional document type hint for all documents
            output_excel: Optional path to export results to Excel
            
        Returns:
            List of extracted data dictionaries
        """
        from utils.export import export_to_excel
        
        dir_path = Path(directory)
        if not dir_path.is_dir():
            raise ValueError(f"Not a directory: {directory}")
        
        results = []
        supported = self.supported_images | self.supported_pdfs
        
        # Find all supported files
        files = [f for f in dir_path.iterdir() if f.suffix.lower() in supported]
        
        # Process each file
        for file_path in files:
            try:
                data = self.extract(str(file_path), document_type)
                data['source_file'] = file_path.name
                results.append(data)
            except Exception as e:
                results.append({
                    'source_file': file_path.name,
                    'error': str(e)
                })
        
        # Export to Excel if requested
        if output_excel and results:
            export_to_excel(results, output_excel)
        
        return results
    
    def detect_document_type(self, file_path: str) -> str:
        """
        Automatically detect the document type.
        
        Uses Vision AI to analyze the document and determine its type.
        
        Args:
            file_path: Path to the document
            
        Returns:
            Detected document type string
        """
        data = self.extract(file_path, document_type='auto')
        return data.get('document_type', 'unknown')
