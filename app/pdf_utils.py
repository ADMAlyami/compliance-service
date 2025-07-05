import pdfplumber
from pdf2image import convert_from_bytes
import pytesseract
import io
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract text from PDF using pdfplumber first, then OCR as fallback.
    
    Args:
        pdf_bytes: PDF file content as bytes
        
    Returns:
        Extracted text as string
    """
    try:
        # Try pdfplumber first for native text extraction
        text = ""
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page_num, page in enumerate(pdf.pages):
                try:
                    page_text = page.extract_text() or ""
                    text += page_text + "\n"
                    logger.debug(f"Extracted {len(page_text)} characters from page {page_num + 1}")
                except Exception as e:
                    logger.warning(f"Error extracting text from page {page_num + 1}: {e}")
                    continue
        
        # If we got substantial text, return it
        if len(text.strip()) > 50:  # Increased threshold for better reliability
            logger.info(f"Successfully extracted {len(text)} characters using pdfplumber")
            return text
        
        # Fallback to OCR if needed
        logger.info("Insufficient text extracted, attempting OCR...")
        return extract_text_with_ocr(pdf_bytes)
        
    except Exception as e:
        logger.error(f"Error in pdfplumber extraction: {e}")
        # Try OCR as last resort
        return extract_text_with_ocr(pdf_bytes)

def extract_text_with_ocr(pdf_bytes: bytes) -> str:
    """
    Extract text from PDF using OCR (Optical Character Recognition).
    
    Args:
        pdf_bytes: PDF file content as bytes
        
    Returns:
        Extracted text as string
    """
    try:
        # Convert PDF to images
        images = convert_from_bytes(pdf_bytes, dpi=300)  # Higher DPI for better OCR
        logger.info(f"Converted PDF to {len(images)} images for OCR")
        
        ocr_text = ""
        for page_num, img in enumerate(images):
            try:
                # Configure OCR for better accuracy
                custom_config = r'--oem 3 --psm 6'  # Use LSTM OCR Engine + Assume uniform block of text
                page_text = pytesseract.image_to_string(img, config=custom_config)
                ocr_text += page_text + "\n"
                logger.debug(f"OCR extracted {len(page_text)} characters from page {page_num + 1}")
            except Exception as e:
                logger.warning(f"Error in OCR for page {page_num + 1}: {e}")
                continue
        
        logger.info(f"OCR completed, extracted {len(ocr_text)} characters total")
        return ocr_text
        
    except Exception as e:
        logger.error(f"Error in OCR extraction: {e}")
        return ""

def get_pdf_info(pdf_bytes: bytes) -> dict:
    """
    Get basic information about the PDF file.
    
    Args:
        pdf_bytes: PDF file content as bytes
        
    Returns:
        Dictionary with PDF information
    """
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            info = {
                "pages": len(pdf.pages),
                "size_bytes": len(pdf_bytes),
                "size_mb": len(pdf_bytes) / (1024 * 1024)
            }
            
            # Try to get PDF metadata
            if hasattr(pdf, 'metadata') and pdf.metadata:
                info["metadata"] = pdf.metadata
                
            return info
    except Exception as e:
        logger.error(f"Error getting PDF info: {e}")
        return {"error": str(e)}
