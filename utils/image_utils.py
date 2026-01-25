"""
Image Processing Utilities

Functions for preprocessing images before OCR/Vision API analysis.
Includes PDF to image conversion and image enhancement.
"""

import os
import tempfile
from typing import Optional, List
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter


def preprocess_image(
    image_path: str,
    max_size: int = 2048,
    enhance_contrast: bool = True
) -> Optional[str]:
    """
    Preprocess an image for better Vision API analysis.
    
    Performs the following operations:
    - Resize if too large (preserves aspect ratio)
    - Convert to RGB mode
    - Optional contrast enhancement
    - Slight sharpening for text clarity
    
    Args:
        image_path: Path to the original image
        max_size: Maximum dimension (width or height)
        enhance_contrast: Whether to apply contrast enhancement
        
    Returns:
        Path to the preprocessed image, or None if preprocessing fails
    """
    try:
        # Open the image
        img = Image.open(image_path)
        
        # Convert to RGB if necessary (handles RGBA, grayscale, etc.)
        if img.mode != 'RGB':
            # Create white background for transparent images
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
                img = background
            else:
                img = img.convert('RGB')
        
        # Resize if too large
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Enhance contrast for better text recognition
        if enhance_contrast:
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.2)  # Slight contrast boost
        
        # Sharpen slightly for text clarity
        img = img.filter(ImageFilter.SHARPEN)
        
        # Save to temporary file
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"preprocessed_{Path(image_path).name}")
        
        # Ensure we save as PNG for quality
        if not temp_path.lower().endswith('.png'):
            temp_path = temp_path.rsplit('.', 1)[0] + '.png'
        
        img.save(temp_path, 'PNG', quality=95)
        
        return temp_path
        
    except Exception as e:
        print(f"Image preprocessing failed: {str(e)}")
        return None


def pdf_to_images(
    pdf_path: str,
    dpi: int = 200,
    first_page_only: bool = False
) -> List[str]:
    """
    Convert a PDF document to images.
    
    Uses pdf2image library which requires poppler to be installed.
    Falls back to a basic method if pdf2image is not available.
    
    Args:
        pdf_path: Path to the PDF file
        dpi: Resolution for conversion (higher = better quality but larger)
        first_page_only: If True, only convert the first page
        
    Returns:
        List of paths to converted images
    """
    try:
        from pdf2image import convert_from_path
        
        # Determine pages to convert
        if first_page_only:
            pages = convert_from_path(pdf_path, dpi=dpi, first_page=1, last_page=1)
        else:
            pages = convert_from_path(pdf_path, dpi=dpi)
        
        # Save each page as a temporary image
        image_paths = []
        temp_dir = tempfile.gettempdir()
        base_name = Path(pdf_path).stem
        
        for i, page in enumerate(pages):
            temp_path = os.path.join(temp_dir, f"{base_name}_page_{i + 1}.png")
            page.save(temp_path, 'PNG')
            image_paths.append(temp_path)
        
        return image_paths
        
    except ImportError:
        print("pdf2image not installed. Install with: pip install pdf2image")
        print("Also requires poppler: https://poppler.freedesktop.org/")
        return []
        
    except Exception as e:
        print(f"PDF conversion failed: {str(e)}")
        return []


def resize_image(image_path: str, max_size: int = 1024) -> str:
    """
    Resize an image to fit within max_size while preserving aspect ratio.
    
    Args:
        image_path: Path to the image
        max_size: Maximum width or height
        
    Returns:
        Path to resized image (may be same as input if no resize needed)
    """
    img = Image.open(image_path)
    
    if max(img.size) <= max_size:
        return image_path
    
    ratio = max_size / max(img.size)
    new_size = tuple(int(dim * ratio) for dim in img.size)
    
    img = img.resize(new_size, Image.Resampling.LANCZOS)
    
    temp_path = os.path.join(tempfile.gettempdir(), f"resized_{Path(image_path).name}")
    img.save(temp_path)
    
    return temp_path


def get_image_info(image_path: str) -> dict:
    """
    Get basic information about an image.
    
    Args:
        image_path: Path to the image
        
    Returns:
        Dictionary with image info (size, mode, format)
    """
    img = Image.open(image_path)
    
    return {
        'width': img.width,
        'height': img.height,
        'mode': img.mode,
        'format': img.format,
        'file_size': os.path.getsize(image_path)
    }
