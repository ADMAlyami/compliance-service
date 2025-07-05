import os
from typing import List

class Settings:
    """Application settings and configuration."""
    
    # API Settings
    API_TITLE: str = "Compliance Document Service"
    API_VERSION: str = "2.0.0"
    API_DESCRIPTION: str = "Automated compliance checking for subcontractor documents"
    
    # File Upload Settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    MAX_FILES_PER_REQUEST: int = 10
    ALLOWED_EXTENSIONS: List[str] = [".pdf"]
    
    # OCR Settings
    OCR_DPI: int = 300
    OCR_CONFIG: str = r'--oem 3 --psm 6'
    
    # Text Extraction Settings
    MIN_TEXT_LENGTH: int = 50  # Minimum characters to consider text extraction successful
    
    # Validation Settings
    EXPIRY_GRACE_PERIOD_DAYS: int = 30
    INSPECTION_VALIDITY_DAYS: int = 365
    
    # Logging Settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # CORS Settings
    CORS_ORIGINS: List[str] = ["*"]  # In production, specify your frontend domain
    
    # Document Type Keywords
    INSURANCE_KEYWORDS: List[str] = [
        "liability insurance", "general liability", "workers compensation",
        "certificate of insurance", "insurance certificate", "policy",
        "coverage", "insured", "insurer", "premium"
    ]
    
    INSPECTION_KEYWORDS: List[str] = [
        "inspection checklist", "inspection sheet", "equipment inspection",
        "safety inspection", "crane inspection", "hoist inspection",
        "inspector", "qualified person", "inspection date"
    ]
    
    TRAINING_KEYWORDS: List[str] = [
        "training card", "osha", "safety training", "certification",
        "worker qualification", "training certificate", "safety card",
        "competent person", "training hours"
    ]
    
    # Required Fields by Document Type
    REQUIRED_FIELDS = {
        "insurance": ["insured", "policy_number"],
        "inspection": ["inspector", "inspection_date"],
        "training": ["worker_name", "certificate_id"]
    }
    
    # Date Formats
    DATE_FORMATS: List[str] = [
        "%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%m-%d-%Y",
        "%d/%m/%y", "%m/%d/%y", "%y-%m-%d", "%d-%m-%y", "%m-%d-%y",
        "%B %d, %Y", "%d %B %Y", "%Y %B %d",
        "%b %d, %Y", "%d %b %Y", "%Y %b %d"
    ]

# Global settings instance
settings = Settings() 