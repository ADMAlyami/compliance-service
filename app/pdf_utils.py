import pdfplumber
from pdf2image import convert_from_bytes
import pytesseract
import io

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    # Try pdfplumber first
    text = ""
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text += page_text + "\n"
    if len(text.strip()) > 30:
        return text
    # Fallback to OCR if needed
    images = convert_from_bytes(pdf_bytes)
    ocr_text = ""
    for img in images:
        ocr_text += pytesseract.image_to_string(img) + "\n"
    return ocr_text
