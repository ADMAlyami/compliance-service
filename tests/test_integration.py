"""
Integration tests for the Compliance Document Service
Tests the most important features using real PDF files
"""

import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app

# Test files directory
TEST_FILES_DIR = Path(__file__).parent.parent / "test_files"


class TestAPIEndpoints:
    """Test the main API endpoints"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_health_endpoint(self, client):
        """Test the health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
    
    def test_root_endpoint_returns_html(self, client):
        """Test that the root endpoint returns HTML"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Compliance Document Checker" in response.text
    
    def test_api_docs_accessible(self, client):
        """Test that API documentation is accessible"""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


class TestDocumentProcessing:
    """Test document processing with real PDF files"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_process_insurance_document(self, client):
        """Test processing an insurance document"""
        pdf_file = TEST_FILES_DIR / "coi_acme_concrete.pdf"
        assert pdf_file.exists(), f"Test file {pdf_file} not found"
        
        with open(pdf_file, "rb") as f:
            files = {"files": ("coi_acme_concrete.pdf", f, "application/pdf")}
            response = client.post("/check-docs", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 1
        
        result = data["results"][0]
        assert result["file"] == "coi_acme_concrete.pdf"
        assert result["doc_type"] == "insurance"
        assert "fields" in result
        assert "verdict" in result
    
    def test_process_training_document(self, client):
        """Test processing a training document"""
        pdf_file = TEST_FILES_DIR / "osha_card_albert_hernandez.pdf"
        assert pdf_file.exists(), f"Test file {pdf_file} not found"
        
        with open(pdf_file, "rb") as f:
            files = {"files": ("osha_card_albert_hernandez.pdf", f, "application/pdf")}
            response = client.post("/check-docs", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 1
        
        result = data["results"][0]
        assert result["file"] == "osha_card_albert_hernandez.pdf"
        assert result["doc_type"] == "training"
        assert "fields" in result
        assert "verdict" in result
    
    def test_process_inspection_document(self, client):
        """Test processing an inspection document"""
        pdf_file = TEST_FILES_DIR / "scaffold_inspection_ST123.pdf"
        assert pdf_file.exists(), f"Test file {pdf_file} not found"
        
        with open(pdf_file, "rb") as f:
            files = {"files": ("scaffold_inspection_ST123.pdf", f, "application/pdf")}
            response = client.post("/check-docs", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 1
        
        result = data["results"][0]
        assert result["file"] == "scaffold_inspection_ST123.pdf"
        assert result["doc_type"] == "inspection"
        assert "fields" in result
        assert "verdict" in result
    
    def test_process_multiple_documents(self, client):
        """Test processing multiple documents at once"""
        pdf_files = [
            TEST_FILES_DIR / "coi_acme_concrete.pdf",
            TEST_FILES_DIR / "osha_card_albert_hernandez.pdf",
            TEST_FILES_DIR / "scaffold_inspection_ST123.pdf"
        ]
        
        # Verify all test files exist
        for pdf_file in pdf_files:
            assert pdf_file.exists(), f"Test file {pdf_file} not found"
        
        files = []
        for pdf_file in pdf_files:
            with open(pdf_file, "rb") as f:
                files.append(("files", (pdf_file.name, f, "application/pdf")))
        
        response = client.post("/check-docs", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 3
        
        # Check that all documents were processed
        doc_types = [result["doc_type"] for result in data["results"]]
        assert "insurance" in doc_types
        assert "training" in doc_types
        assert "inspection" in doc_types


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_no_files_provided(self, client):
        """Test API behavior when no files are provided"""
        response = client.post("/check-docs")
        assert response.status_code == 422  # Validation error
    
    def test_invalid_file_type(self, client):
        """Test API behavior with invalid file type"""
        # Create a temporary text file
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"This is not a PDF file")
            temp_file = f.name
        
        try:
            with open(temp_file, "rb") as f:
                files = {"files": ("test.txt", f, "text/plain")}
                response = client.post("/check-docs", files=files)
            
            assert response.status_code == 400  # Bad request
        finally:
            os.unlink(temp_file)
    
    def test_large_file_rejection(self, client):
        """Test that large files are rejected"""
        # Create a large file (larger than 10MB)
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            # Write 11MB of data
            f.write(b"0" * (11 * 1024 * 1024))
            temp_file = f.name
        
        try:
            with open(temp_file, "rb") as f:
                files = {"files": ("large_file.pdf", f, "application/pdf")}
                response = client.post("/check-docs", files=files)
            
            assert response.status_code == 400  # File too large
        finally:
            os.unlink(temp_file)


class TestFieldExtraction:
    """Test field extraction accuracy"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_insurance_field_extraction(self, client):
        """Test that insurance documents extract expected fields"""
        pdf_file = TEST_FILES_DIR / "coi_acme_concrete.pdf"
        
        with open(pdf_file, "rb") as f:
            files = {"files": ("coi_acme_concrete.pdf", f, "application/pdf")}
            response = client.post("/check-docs", files=files)
        
        assert response.status_code == 200
        data = response.json()
        result = data["results"][0]
        
        # Check that expected fields are extracted
        fields = result["fields"]
        expected_fields = ["insured", "policy_number", "insurer", "coverage_type", "effective_date", "expiry_date"]
        
        for field in expected_fields:
            assert field in fields, f"Expected field '{field}' not found"
            assert "value" in fields[field]
            assert "confidence" in fields[field]
            assert 0.0 <= fields[field]["confidence"] <= 1.0
    
    def test_training_field_extraction(self, client):
        """Test that training documents extract expected fields"""
        pdf_file = TEST_FILES_DIR / "osha_card_albert_hernandez.pdf"
        
        with open(pdf_file, "rb") as f:
            files = {"files": ("osha_card_albert_hernandez.pdf", f, "application/pdf")}
            response = client.post("/check-docs", files=files)
        
        assert response.status_code == 200
        data = response.json()
        result = data["results"][0]
        
        # Check that expected fields are extracted
        fields = result["fields"]
        expected_fields = ["worker_name", "certificate_id", "hours", "issue_date", "expiry_date", "issued_by"]
        
        for field in expected_fields:
            assert field in fields, f"Expected field '{field}' not found"
            assert "value" in fields[field]
            assert "confidence" in fields[field]
            assert 0.0 <= fields[field]["confidence"] <= 1.0
    
    def test_inspection_field_extraction(self, client):
        """Test that inspection documents extract expected fields"""
        pdf_file = TEST_FILES_DIR / "scaffold_inspection_ST123.pdf"
        
        with open(pdf_file, "rb") as f:
            files = {"files": ("scaffold_inspection_ST123.pdf", f, "application/pdf")}
            response = client.post("/check-docs", files=files)
        
        assert response.status_code == 200
        data = response.json()
        result = data["results"][0]
        
        # Check that expected fields are extracted
        fields = result["fields"]
        expected_fields = ["inspector", "inspection_date", "equipment_id", "result"]
        
        for field in expected_fields:
            assert field in fields, f"Expected field '{field}' not found"
            assert "value" in fields[field]
            assert "confidence" in fields[field]
            assert 0.0 <= fields[field]["confidence"] <= 1.0


class TestDocumentTypeDetection:
    """Test document type detection accuracy"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_all_document_types_detected(self, client):
        """Test that all document types are correctly detected"""
        test_files = {
            "coi_acme_concrete.pdf": "insurance",
            "coi_bolt_electric.pdf": "insurance",
            "osha_card_albert_hernandez.pdf": "training",
            "osha_card_nadia_hussain.pdf": "training",
            "crane_inspection_CRN812.pdf": "inspection",
            "scaffold_inspection_ST123.pdf": "inspection"
        }
        
        for filename, expected_type in test_files.items():
            pdf_file = TEST_FILES_DIR / filename
            assert pdf_file.exists(), f"Test file {pdf_file} not found"
            
            with open(pdf_file, "rb") as f:
                files = {"files": (filename, f, "application/pdf")}
                response = client.post("/check-docs", files=files)
            
            assert response.status_code == 200
            data = response.json()
            result = data["results"][0]
            
            assert result["doc_type"] == expected_type, \
                f"Expected {expected_type} for {filename}, got {result['doc_type']}"


class TestValidationLogic:
    """Test validation logic and verdicts"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_validation_verdicts_present(self, client):
        """Test that all results have validation verdicts"""
        pdf_files = list(TEST_FILES_DIR.glob("*.pdf"))
        
        for pdf_file in pdf_files:
            with open(pdf_file, "rb") as f:
                files = {"files": (pdf_file.name, f, "application/pdf")}
                response = client.post("/check-docs", files=files)
            
            assert response.status_code == 200
            data = response.json()
            result = data["results"][0]
            
            assert "verdict" in result
            assert result["verdict"] in ["pass", "fail", "unknown"], \
                f"Invalid verdict '{result['verdict']}' for {pdf_file.name}"
    
    def test_confidence_scores_valid(self, client):
        """Test that confidence scores are within valid range"""
        pdf_file = TEST_FILES_DIR / "coi_acme_concrete.pdf"
        
        with open(pdf_file, "rb") as f:
            files = {"files": ("coi_acme_concrete.pdf", f, "application/pdf")}
            response = client.post("/check-docs", files=files)
        
        assert response.status_code == 200
        data = response.json()
        result = data["results"][0]
        
        for field_name, field_data in result["fields"].items():
            assert "confidence" in field_data
            confidence = field_data["confidence"]
            assert 0.0 <= confidence <= 1.0, \
                f"Confidence score {confidence} for field '{field_name}' is out of range" 