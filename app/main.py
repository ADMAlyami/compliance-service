from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import logging
from typing import List
import os

from app.pdf_utils import extract_text_from_pdf
from app.parser import parse_document_type, parse_fields
from app.validator import validate_fields
from app.models import DocumentResult, FieldResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Compliance Document Service", version="2.0.0")

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".pdf"}

def validate_file(file: UploadFile) -> None:
    """Validate uploaded file"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Only PDF files are allowed. Got: {file_ext}"
        )

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the frontend HTML"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Compliance Document Checker</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            .header p {
                opacity: 0.9;
                font-size: 1.1em;
            }
            .content {
                padding: 40px;
            }
            .upload-area {
                border: 3px dashed #ddd;
                border-radius: 10px;
                padding: 40px;
                text-align: center;
                margin-bottom: 30px;
                transition: all 0.3s ease;
                cursor: pointer;
            }
            .upload-area:hover {
                border-color: #667eea;
                background: #f8f9ff;
            }
            .upload-area.dragover {
                border-color: #667eea;
                background: #f0f4ff;
            }
            .file-input {
                display: none;
            }
            .btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 25px;
                font-size: 1.1em;
                cursor: pointer;
                transition: all 0.3s ease;
                margin: 10px;
            }
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
            }
            .btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }
            .file-list {
                margin: 20px 0;
                text-align: left;
            }
            .file-item {
                background: #f8f9fa;
                padding: 10px 15px;
                margin: 5px 0;
                border-radius: 5px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .remove-file {
                background: #dc3545;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                cursor: pointer;
            }
            .results {
                margin-top: 30px;
            }
            .result-card {
                background: #f8f9fa;
                border-radius: 10px;
                padding: 20px;
                margin: 15px 0;
                border-left: 5px solid #667eea;
            }
            .result-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
            }
            .verdict {
                padding: 5px 15px;
                border-radius: 20px;
                font-weight: bold;
                text-transform: uppercase;
            }
            .verdict.pass {
                background: #d4edda;
                color: #155724;
            }
            .verdict.fail {
                background: #f8d7da;
                color: #721c24;
            }
            .verdict.unknown {
                background: #fff3cd;
                color: #856404;
            }
            .field-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px;
                margin-top: 15px;
            }
            .field-item {
                background: white;
                padding: 15px;
                border-radius: 8px;
                border: 1px solid #e9ecef;
            }
            .field-label {
                font-weight: bold;
                color: #495057;
                margin-bottom: 5px;
            }
            .field-value {
                color: #212529;
                margin-bottom: 5px;
            }
            .confidence {
                font-size: 0.9em;
                color: #6c757d;
            }
            .loading {
                text-align: center;
                padding: 40px;
                color: #667eea;
            }
            .error {
                background: #f8d7da;
                color: #721c24;
                padding: 15px;
                border-radius: 8px;
                margin: 20px 0;
            }
            .success {
                background: #d4edda;
                color: #155724;
                padding: 15px;
                border-radius: 8px;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📋 Compliance Document Checker</h1>
                <p>Upload PDF documents to check compliance automatically</p>
            </div>
            
            <div class="content">
                <div class="upload-area" id="uploadArea">
                    <h3>📁 Drop PDF files here or click to browse</h3>
                    <p>Supports: Insurance certificates, Inspection sheets, OSHA training cards</p>
                    <input type="file" id="fileInput" class="file-input" multiple accept=".pdf">
                    <button class="btn" onclick="document.getElementById('fileInput').click()">
                        Choose Files
                    </button>
                </div>
                
                <div id="fileList" class="file-list"></div>
                
                <button id="processBtn" class="btn" onclick="processFiles()" disabled>
                    Process Documents
                </button>
                
                <div id="loading" class="loading" style="display: none;">
                    <h3>🔄 Processing documents...</h3>
                    <p>This may take a few moments for large files</p>
                </div>
                
                <div id="results" class="results"></div>
            </div>
        </div>

        <script>
            let selectedFiles = [];
            
            // Drag and drop functionality
            const uploadArea = document.getElementById('uploadArea');
            const fileInput = document.getElementById('fileInput');
            
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('dragover');
            });
            
            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('dragover');
            });
            
            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
                const files = Array.from(e.dataTransfer.files).filter(f => f.type === 'application/pdf');
                addFiles(files);
            });
            
            fileInput.addEventListener('change', (e) => {
                addFiles(Array.from(e.target.files));
            });
            
            function addFiles(files) {
                files.forEach(file => {
                    if (!selectedFiles.find(f => f.name === file.name)) {
                        selectedFiles.push(file);
                    }
                });
                updateFileList();
                updateProcessButton();
            }
            
            function removeFile(fileName) {
                selectedFiles = selectedFiles.filter(f => f.name !== fileName);
                updateFileList();
                updateProcessButton();
            }
            
            function updateFileList() {
                const fileList = document.getElementById('fileList');
                if (selectedFiles.length === 0) {
                    fileList.innerHTML = '';
                    return;
                }
                
                fileList.innerHTML = '<h4>Selected Files:</h4>';
                selectedFiles.forEach(file => {
                    const fileItem = document.createElement('div');
                    fileItem.className = 'file-item';
                    fileItem.innerHTML = `
                        <span>${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)</span>
                        <button class="remove-file" onclick="removeFile('${file.name}')">Remove</button>
                    `;
                    fileList.appendChild(fileItem);
                });
            }
            
            function updateProcessButton() {
                const processBtn = document.getElementById('processBtn');
                processBtn.disabled = selectedFiles.length === 0;
            }
            
            async function processFiles() {
                if (selectedFiles.length === 0) return;
                
                const loading = document.getElementById('loading');
                const results = document.getElementById('results');
                const processBtn = document.getElementById('processBtn');
                
                loading.style.display = 'block';
                results.innerHTML = '';
                processBtn.disabled = true;
                
                try {
                    const formData = new FormData();
                    selectedFiles.forEach(file => {
                        formData.append('files', file);
                    });
                    
                    const response = await fetch('/check-docs', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    
                    const data = await response.json();
                    displayResults(data.results);
                    
                } catch (error) {
                    console.error('Error:', error);
                    results.innerHTML = `
                        <div class="error">
                            <h4>❌ Error Processing Files</h4>
                            <p>${error.message}</p>
                        </div>
                    `;
                } finally {
                    loading.style.display = 'none';
                    processBtn.disabled = false;
                }
            }
            
            function displayResults(results) {
                const resultsDiv = document.getElementById('results');
                
                if (results.length === 0) {
                    resultsDiv.innerHTML = '<div class="error">No results returned</div>';
                    return;
                }
                
                resultsDiv.innerHTML = '<h3>📊 Analysis Results</h3>';
                
                results.forEach(result => {
                    const resultCard = document.createElement('div');
                    resultCard.className = 'result-card';
                    
                    const fieldsHtml = Object.entries(result.fields).map(([key, field]) => `
                        <div class="field-item">
                            <div class="field-label">${key.replace(/_/g, ' ').toUpperCase()}</div>
                            <div class="field-value">${field.value || 'Not found'}</div>
                            <div class="confidence">Confidence: ${(field.confidence * 100).toFixed(1)}%</div>
                        </div>
                    `).join('');
                    
                    resultCard.innerHTML = `
                        <div class="result-header">
                            <h4>📄 ${result.file}</h4>
                            <span class="verdict ${result.verdict}">${result.verdict}</span>
                        </div>
                        <p><strong>Document Type:</strong> ${result.doc_type}</p>
                        <div class="field-grid">
                            ${fieldsHtml}
                        </div>
                    `;
                    
                    resultsDiv.appendChild(resultCard);
                });
            }
        </script>
    </body>
    </html>
    """

@app.post("/check-docs")
async def check_docs(files: List[UploadFile] = File(...)):
    """Process uploaded PDF files for compliance checking"""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    if len(files) > 10:  # Limit number of files
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed per request")
    
    results = []
    
    for file in files:
        try:
            # Validate file
            validate_file(file)
            
            # Check file size
            content = await file.read()
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400, 
                    detail=f"File {file.filename} too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
                )
            
            logger.info(f"Processing file: {file.filename}")
            
            # Extract text from PDF
            text = extract_text_from_pdf(content)
            if not text.strip():
                logger.warning(f"No text extracted from {file.filename}")
                results.append(DocumentResult(
                    file=file.filename,
                    doc_type="unknown",
                    fields={},
                    verdict="fail"
                ))
                continue
            
            # Parse document type and fields
            doc_type = parse_document_type(text)
            fields, confidences = parse_fields(text, doc_type)
            
            # Validate fields
            verdict = validate_fields(fields, doc_type)
            
            # Create field results
            fields_result = {
                k: FieldResult(value=v, confidence=confidences.get(k, 0.0)) 
                for k, v in fields.items()
            }
            
            results.append(DocumentResult(
                file=file.filename,
                doc_type=doc_type,
                fields=fields_result,
                verdict=verdict
            ))
            
            logger.info(f"Successfully processed {file.filename}: {doc_type} - {verdict}")
            
        except Exception as e:
            logger.error(f"Error processing {file.filename}: {str(e)}")
            results.append(DocumentResult(
                file=file.filename,
                doc_type="error",
                fields={},
                verdict="fail"
            ))
    
    return {"results": results}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "compliance-document-checker"}
