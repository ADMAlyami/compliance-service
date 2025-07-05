"""
Pytest configuration and fixtures for Compliance Document Service tests
"""

import pytest
import asyncio
from pathlib import Path
from httpx import AsyncClient
from fastapi.testclient import TestClient

# Import the FastAPI app
from app.main import app

# Test files directory
TEST_FILES_DIR = Path(__file__).parent.parent / "test_files"

@pytest.fixture
def test_files_dir():
    """Return the path to test files directory"""
    return TEST_FILES_DIR

@pytest.fixture
def sample_pdf_files(test_files_dir):
    """Return list of available test PDF files"""
    pdf_files = list(test_files_dir.glob("*.pdf"))
    return pdf_files

@pytest.fixture
def insurance_pdf_files(test_files_dir):
    """Return insurance-related test PDF files"""
    insurance_files = [
        test_files_dir / "coi_acme_concrete.pdf",
        test_files_dir / "coi_bolt_electric.pdf"
    ]
    return [f for f in insurance_files if f.exists()]

@pytest.fixture
def training_pdf_files(test_files_dir):
    """Return training-related test PDF files"""
    training_files = [
        test_files_dir / "osha_card_albert_hernandez.pdf",
        test_files_dir / "osha_card_nadia_hussain.pdf"
    ]
    return [f for f in training_files if f.exists()]

@pytest.fixture
def inspection_pdf_files(test_files_dir):
    """Return inspection-related test PDF files"""
    inspection_files = [
        test_files_dir / "crane_inspection_CRN812.pdf",
        test_files_dir / "scaffold_inspection_ST123.pdf"
    ]
    return [f for f in inspection_files if f.exists()]

@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)

@pytest.fixture
async def async_client():
    """Create an async test client for the FastAPI app"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def sample_insurance_text():
    """Sample insurance document text for testing"""
    return """
    CERTIFICATE OF INSURANCE
    
    INSURED: ACME Construction LLC
    POLICY NUMBER: GL-1234567-2024
    INSURER: ABC Insurance Company
    COVERAGE TYPE: General Liability
    EFFECTIVE DATE: 01/01/2024
    EXPIRY DATE: 12/31/2024
    
    This certificate provides evidence of insurance coverage.
    """

@pytest.fixture
def sample_inspection_text():
    """Sample inspection document text for testing"""
    return """
    EQUIPMENT INSPECTION CHECKLIST
    
    INSPECTOR: John Smith
    INSPECTION DATE: 15/06/2024
    EQUIPMENT ID: CRN-812
    RESULT: PASS
    
    All safety checks completed successfully.
    """

@pytest.fixture
def sample_training_text():
    """Sample training document text for testing"""
    return """
    OSHA TRAINING CERTIFICATE
    
    WORKER NAME: Albert Hernandez
    CERTIFICATE ID: OSHA-2024-001
    HOURS: 40
    ISSUE DATE: 01/03/2024
    EXPIRY DATE: 01/03/2025
    ISSUED BY: Safety Training Institute
    """

@pytest.fixture
def mock_pdf_bytes():
    """Mock PDF bytes for testing"""
    return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Test PDF Content) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000204 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n297\n%%EOF\n"

# Configure pytest
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )

# Async test support
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close() 