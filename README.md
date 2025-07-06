# 📋  Documents Compliance Checks Microservice

A robust, production-ready microservice that automates compliance checks on subcontractor documents including insurance certificates, equipment inspection sheets, and OSHA training cards. Features a beautiful web interface and enhanced processing capabilities.

## ✨ Enhanced Features

### Core Functionality
- **Multi-file Processing**: Upload and process multiple PDF files simultaneously
- **Robust Validation**: Comprehensive compliance rules with grace periods
- **Beautiful Web UI**



### Document Types Supported
1. **Insurance Certificates**: Liability insurance, workers compensation, etc.
2. **Inspection Sheets**: Equipment inspections, safety checks, etc.
3. **Training Cards**: OSHA training, safety certifications, etc.

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+**
2. **Tesseract OCR** (required for image-based PDFs)

### Installation

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd compliance-service
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Tesseract OCR:**
   
   **macOS:**
   ```bash
   brew install tesseract
   ```
   
   **Ubuntu/Debian:**
   ```bash
   sudo apt-get update
   sudo apt-get install tesseract-ocr
   ```
   
   **Windows:**
   - Download from [UB Mannheim Tesseract releases](https://github.com/UB-Mannheim/tesseract/wiki)
   - Add to PATH environment variable

4. **Start the service:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access the application:**
   - **Web Interface**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs
   - **Health Check**: http://localhost:8000/health

## 🧪 Testing

### Running Tests

The project includes comprehensive integration tests that use real PDF files from the `test_files` directory.

#### Quick Test
Run a quick test to verify the service is working:
```bash
python run_tests.py --quick
```

#### Full Test Suite
Run the complete integration test suite:
```bash
python run_tests.py
```

#### Using Pytest Directly
For more detailed test output:
```bash
pytest tests/test_integration.py -v
```

### Test Coverage

The test suite covers:
- ✅ **API Endpoints**: Health checks, web interface, documentation
- ✅ **Document Processing**: Insurance, training, and inspection documents
- ✅ **Field Extraction**: Verification of extracted fields and confidence scores
- ✅ **Document Type Detection**: Accuracy of document classification
- ✅ **Error Handling**: Invalid files, missing files, large files
- ✅ **Validation Logic**: Compliance verdicts and confidence scoring

### Test Files

The `test_files` directory contains sample PDF documents for testing:
- `coi_acme_concrete.pdf` - Insurance certificate
- `coi_bolt_electric.pdf` - Insurance certificate
- `crane_inspection_CRN812.pdf` - Equipment inspection
- `osha_card_albert_hernandez.pdf` - Training certificate
- `osha_card_nadia_hussain.pdf` - Training certificate
- `scaffold_inspection_ST123.pdf` - Equipment inspection

## 🎯 Usage

### Web Interface
1. Open http://localhost:8000 in your browser
2. Drag and drop PDF files or click to browse
3. Click "Process Documents" to analyze
4. View results with confidence scores and compliance verdicts

### API Usage

#### Upload Documents
```bash
curl -X POST "http://localhost:8000/check-docs" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@document1.pdf" \
  -F "files=@document2.pdf"
```

#### Response Format
```json
{
  "results": [
    {
      "file": "insurance_certificate.pdf",
      "doc_type": "insurance",
      "fields": {
        "insured": {
          "value": "ACME Construction LLC",
          "confidence": 0.95
        },
        "policy_number": {
          "value": "GL-1234567-2024",
          "confidence": 0.92
        },
        "expiry_date": {
          "value": "12/31/2024",
          "confidence": 0.88
        }
      },
      "verdict": "pass"
    }
  ]
}
```

## 🔧 Configuration

The application uses a centralized configuration system. Key settings can be modified in `app/config.py`:

```python
# File upload limits
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_FILES_PER_REQUEST = 10

# OCR settings
OCR_DPI = 300
OCR_CONFIG = r'--oem 3 --psm 6'

# Validation settings
EXPIRY_GRACE_PERIOD_DAYS = 30
INSPECTION_VALIDITY_DAYS = 365
```

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface |
| `/check-docs` | POST | Process PDF documents |
| `/health` | GET | Health check |
| `/docs` | GET | Interactive API documentation |

## 🏗️ Architecture

### Components
- **FastAPI**: High-performance web framework
- **pdfplumber**: Native PDF text extraction
- **pytesseract**: OCR for image-based documents
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server

### Processing Pipeline
1. **File Validation**: Check file type, size, and format
2. **Text Extraction**: Use pdfplumber, fallback to OCR
3. **Document Classification**: Identify document type using keyword scoring
4. **Field Extraction**: Apply regex patterns with confidence scoring
5. **Validation**: Check compliance rules and expiry dates
6. **Result Generation**: Return structured results with confidence scores

## 🔍 Field Extraction

### Insurance Documents
- Insured name/company
- Policy number
- Insurance company
- Coverage type
- Effective date
- Expiry date

### Inspection Documents
- Inspector name
- Inspection date
- Equipment ID
- Inspection result (PASS/FAIL)

### Training Documents
- Worker name
- Certificate ID
- Training hours
- Issue date
- Expiry date
- Issuing organization

## 🛡️ Security & Validation

### Input Validation
- File type restrictions (PDF only)
- File size limits (configurable)
- Maximum files per request
- Malicious file detection

### Error Handling
- Graceful degradation for OCR failures
- Detailed error logging
- User-friendly error messages
- Fallback processing strategies

## 📈 Performance

### Optimizations
- Asynchronous file processing
- Efficient OCR configuration
- Intelligent text extraction thresholds
- Memory-efficient PDF handling

### Monitoring
- Request/response logging
- Processing time tracking
- Error rate monitoring
- Health check endpoints

## 🚀 Deployment

### Docker (Recommended)
```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables
```bash
LOG_LEVEL=INFO
MAX_FILE_SIZE=10485760
MAX_FILES_PER_REQUEST=10
```

## 🔧 Troubleshooting

### Common Issues

**OCR not working:**
- Ensure Tesseract is installed and in PATH
- Check OCR configuration in settings

**File upload errors:**
- Verify file size limits
- Check file format (PDF only)
- Review CORS settings

**Poor extraction accuracy:**
- Adjust OCR DPI settings
- Review regex patterns
- Check document quality

**Test failures:**
- Ensure test PDF files are in the `test_files` directory
- Check that all dependencies are installed
- Verify Tesseract OCR is working

### Logs
Enable debug logging:
```bash
LOG_LEVEL=DEBUG uvicorn app.main:app --reload
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Run the test suite: `python run_tests.py`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the API documentation
3. Run the test suite to verify functionality
4. Open an issue on GitHub

---

**Built with ❤️**




