# Subcontractor Compliance Document Microservice

## Objective

This project is a proof-of-concept microservice that automates compliance checks on subcontractor documents such as insurance certificates, equipment inspection sheets, and OSHA training cards. The system processes uploaded PDF files, extracts and validates key fields, and returns a structured compliance verdict.

---

## Features

- Exposes a REST endpoint `/check-docs` for PDF file uploads (supports one or more files at a time)
- Extracts text using native PDF parsing with OCR fallback for scanned or low-quality files
- Parses key fields:
  - Worker or company name
  - Document type (insurance, inspection, training)
  - Issue and expiry dates
  - Policy or certificate numbers
  - Equipment ID (for inspection sheets)
- Applies validation rules (e.g., not expired, required fields present, formats correct)
- Assigns a confidence score to each extracted field
- Returns results as JSON including extracted fields, confidence scores, and pass/fail verdict

## Architecture & Design Choices
Framework:
FastAPI is used for its speed, simplicity, and built-in API documentation.

Text Extraction:
pdfplumber is used for native PDF text extraction. If text extraction fails or yields little content, OCR is performed using pytesseract and pdf2image to handle scanned/image-based documents.

Field Parsing:
Regular expressions and rules-based logic are used to extract structured fields from semi-structured documents. This approach is transparent and easy to extend for more document types.

Validation:
Validation rules are applied based on document type (such as checking expiry dates, presence of required fields, and format correctness).

Confidence Scoring:
Confidence is assigned heuristically based on field extraction success, allowing users to assess data reliability.

Stateless Microservice:
The API is stateless; no documents or results are stored. This makes the service scalable and suitable for containerization or deployment in serverless environments.

Multi-file Support:
The /check-docs endpoint is designed to accept and process multiple files in one request, providing a result for each file in the response.

## Potential Improvements
Use ML/NLP-based entity extraction for greater accuracy with more varied or complex document layouts.

Add a simple web-based user interface for manual uploads and visual review.

Extend support for direct image files (JPG, PNG, TIFF).

Implement more robust document type detection and validation based on project-specific requirements.

Add logging, audit trails, and error monitoring for compliance and debugging.

Provide deployment scripts for cloud platforms and add CI/CD integration for easier updates and reliability.

Implement user authentication or API key support for production deployments.


---

## Setup Instructions

1. **Clone the repository**
    ```bash
    git clone https://github.com/yourusername/compliance-service.git
    cd compliance-service
    ```

2. **Install Python dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3. **Install Tesseract OCR (system dependency)**
    - **macOS:** `brew install tesseract`
    - **Ubuntu:** `sudo apt-get install tesseract-ocr`
    - **Windows:** Download from [UB Mannheim Tesseract releases](https://github.com/UB-Mannheim/tesseract/wiki)

4. **Start the service**
    ```bash
    uvicorn app.main:app --reload
    ```
    By default, the API runs at `http://127.0.0.1:8000`.

5. **Test the API**
    - Use the interactive docs at `http://127.0.0.1:8000/docs`
    - Or submit a `POST` request to `/check-docs` with one or more PDF files attached as form-data.



---

## API Usage

### Endpoint

- **POST** `/check-docs`

**Request:**  
- Form field: `files`
- Value: One or more PDF files

**Response Example:**
```json
{
  "results": [
    {
      "file": "sample.pdf",
      "doc_type": "insurance",
      "fields": {
        "insured": {"value": "ACME Concrete LLC", "confidence": 0.95},
        "policy_number": {"value": "GL-1234567-2024", "confidence": 0.95},
        "expiry_date": {"value": "06/01/2025", "confidence": 0.95}
      },
      "verdict": "pass"
    }
  ]
}




