import re
import logging
from typing import Dict, Tuple, List
from datetime import datetime

logger = logging.getLogger(__name__)

# Enhanced regex patterns with multiple variations
INSURANCE_PATTERNS = {
    "insured": [
        r"INSURED:\s*([^\n\r]+)",
        r"INSURED\s+NAME:\s*([^\n\r]+)",
        r"NAMED\s+INSURED:\s*([^\n\r]+)",
        r"COMPANY:\s*([^\n\r]+)",
        r"BUSINESS\s+NAME:\s*([^\n\r]+)"
    ],
    "policy_number": [
        r"POLICY\s+NUMBER:\s*([^\n\r]+)",
        r"POLICY\s+#:\s*([^\n\r]+)",
        r"POLICY\s+NO:\s*([^\n\r]+)",
        r"CERTIFICATE\s+NUMBER:\s*([^\n\r]+)"
    ],
    "insurer": [
        r"INSURER:\s*([^\n\r]+)",
        r"INSURANCE\s+COMPANY:\s*([^\n\r]+)",
        r"CARRIER:\s*([^\n\r]+)",
        r"PROVIDER:\s*([^\n\r]+)"
    ],
    "coverage_type": [
        r"COVERAGE\s+TYPE:\s*([^\n\r]+)",
        r"TYPE\s+OF\s+COVERAGE:\s*([^\n\r]+)",
        r"INSURANCE\s+TYPE:\s*([^\n\r]+)"
    ],
    "effective_date": [
        r"EFFECTIVE\s+DATE:\s*([\d\/\-]+)",
        r"INCEPTION\s+DATE:\s*([\d\/\-]+)",
        r"START\s+DATE:\s*([\d\/\-]+)",
        r"FROM:\s*([\d\/\-]+)"
    ],
    "expiry_date": [
        r"EXPIRY\s+DATE:\s*([^\n\r]+)",
        r"EXPIRATION\s+DATE:\s*([^\n\r]+)",
        r"EXPIRATION:\s*([^\n\r]+)",
        r"UNTIL:\s*([^\n\r]+)",
        r"END\s+DATE:\s*([^\n\r]+)",
        r"TO:\s*([^\n\r]+)",
        r"EXPIRES:\s*([^\n\r]+)",
        r"VALID\s+UNTIL:\s*([^\n\r]+)"
    ]
}

INSPECTION_PATTERNS = {
    "inspector": [
        r"INSPECTOR:\s*([^\n\r]+)",
        r"INSPECTED\s+BY:\s*([^\n\r]+)",
        r"QUALIFIED\s+PERSON:\s*([^\n\r]+)"
    ],
    "inspection_date": [
        r"INSPECTION\s+DATE:\s*([^\n\r]+)",
        r"DATE\s+OF\s+INSPECTION:\s*([^\n\r]+)",
        r"INSPECTED\s+ON:\s*([^\n\r]+)"
    ],
    "equipment_id": [
        r"(CRANE|EQUIPMENT)\s+ID:\s*([^\n\r]+)",
        r"SERIAL\s+NUMBER:\s*([^\n\r]+)",
        r"EQUIPMENT\s+NUMBER:\s*([^\n\r]+)",
        r"MODEL\s+NUMBER:\s*([^\n\r]+)"
    ],
    "result": [
        r"RESULT:\s*(PASS|FAIL)",
        r"STATUS:\s*(PASS|FAIL)",
        r"INSPECTION\s+RESULT:\s*(PASS|FAIL)",
        r"CONDITION:\s*(PASS|FAIL)"
    ]
}

TRAINING_PATTERNS = {
    "worker_name": [
        r"WORKER\s+NAME:\s*([^\n\r]+)",
        r"EMPLOYEE\s+NAME:\s*([^\n\r]+)",
        r"NAME:\s*([^\n\r]+)",
        r"TRAINEE:\s*([^\n\r]+)"
    ],
    "certificate_id": [
        r"CERTIFICATE\s+ID:\s*([^\n\r]+)",
        r"CARD\s+NUMBER:\s*([^\n\r]+)",
        r"ID\s+NUMBER:\s*([^\n\r]+)",
        r"LICENSE\s+NUMBER:\s*([^\n\r]+)"
    ],
    "hours": [
        r"HOURS:\s*([^\n\r]+)",
        r"TRAINING\s+HOURS:\s*([^\n\r]+)",
        r"DURATION:\s*([^\n\r]+)"
    ],
    "issue_date": [
        r"ISSUE\s+DATE:\s*([^\n\r]+)",
        r"DATE\s+ISSUED:\s*([^\n\r]+)",
        r"ISSUED\s+ON:\s*([^\n\r]+)"
    ],
    "expiry_date": [
        r"EXPIRY\s+DATE:\s*([^\n\r]+)",
        r"EXPIRATION\s+DATE:\s*([^\n\r]+)",
        r"VALID\s+UNTIL:\s*([^\n\r]+)"
    ],
    "issued_by": [
        r"ISSUED\s+BY:\s*([^\n\r]+)",
        r"TRAINING\s+PROVIDER:\s*([^\n\r]+)",
        r"ORGANIZATION:\s*([^\n\r]+)"
    ]
}

def parse_document_type(text: str) -> str:
    """
    Enhanced document type detection with confidence scoring.
    
    Args:
        text: Extracted text from document
        
    Returns:
        Document type string
    """
    text_lower = text.lower()
    
    # Score-based detection
    scores = {
        "insurance": 0,
        "inspection": 0,
        "training": 0
    }
    
    # Insurance keywords
    insurance_keywords = [
        "liability insurance", "general liability", "workers compensation",
        "certificate of insurance", "insurance certificate", "policy",
        "coverage", "insured", "insurer", "premium"
    ]
    
    # Inspection keywords
    inspection_keywords = [
        "inspection checklist", "inspection sheet", "equipment inspection",
        "safety inspection", "crane inspection", "hoist inspection",
        "inspector", "qualified person", "inspection date"
    ]
    
    # Training keywords
    training_keywords = [
        "training card", "osha", "safety training", "certification",
        "worker qualification", "training certificate", "safety card",
        "competent person", "training hours"
    ]
    
    # Calculate scores
    for keyword in insurance_keywords:
        if keyword in text_lower:
            scores["insurance"] += 1
    
    for keyword in inspection_keywords:
        if keyword in text_lower:
            scores["inspection"] += 1
    
    for keyword in training_keywords:
        if keyword in text_lower:
            scores["training"] += 1
    
    # Return the type with highest score, or "unknown" if no clear match
    max_score = max(scores.values())
    if max_score > 0:
        for doc_type, score in scores.items():
            if score == max_score:
                logger.info(f"Detected document type: {doc_type} (score: {score})")
                return doc_type
    
    logger.warning("Could not determine document type")
    return "unknown"

def extract_field_with_patterns(text: str, patterns: List[str]) -> Tuple[str | None, float]:
    """
    Extract a field using multiple regex patterns and return the best match.
    
    Args:
        text: Text to search in
        patterns: List of regex patterns to try
        
    Returns:
        Tuple of (extracted_value, confidence_score)
    """
    for pattern in patterns:
        try:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                value = match.group(1).strip()
                if value and len(value) > 0:
                    # Calculate confidence based on pattern complexity and match quality
                    confidence = calculate_confidence(pattern, value, text)
                    return value, confidence
        except Exception as e:
            logger.debug(f"Error with pattern {pattern}: {e}")
            continue
    
    return None, 0.0

def calculate_confidence(pattern: str, value: str, context: str) -> float:
    """
    Calculate confidence score for extracted field.
    
    Args:
        pattern: Regex pattern used
        value: Extracted value
        context: Surrounding text context
        
    Returns:
        Confidence score between 0.0 and 1.0
    """
    base_confidence = 0.8
    
    # Adjust based on value quality
    if len(value) < 2:
        base_confidence -= 0.3
    elif len(value) > 100:
        base_confidence -= 0.2
    
    # Adjust based on pattern specificity
    if ":" in pattern:
        base_confidence += 0.1
    
    # Adjust based on context
    if value.lower() in ["n/a", "none", "unknown", "tbd"]:
        base_confidence -= 0.4
    
    # Ensure confidence is within bounds
    return max(0.0, min(1.0, base_confidence))

def parse_fields(text: str, doc_type: str) -> Tuple[Dict[str, str], Dict[str, float]]:
    """
    Parse fields from document text based on document type.
    
    Args:
        text: Extracted text from document
        doc_type: Type of document
        
    Returns:
        Tuple of (fields_dict, confidence_dict)
    """
    fields = {}
    confidence = {}
    
    try:
        if doc_type == "insurance":
            patterns = INSURANCE_PATTERNS
        elif doc_type == "inspection":
            patterns = INSPECTION_PATTERNS
        elif doc_type == "training":
            patterns = TRAINING_PATTERNS
        else:
            logger.warning(f"Unknown document type: {doc_type}")
            return fields, confidence
        
        # Extract each field
        for field_name, field_patterns in patterns.items():
            value, conf = extract_field_with_patterns(text, field_patterns)
            if value is not None:
                fields[field_name] = value
                confidence[field_name] = conf
                logger.debug(f"Extracted {field_name}: {value} (confidence: {conf:.2f})")
        
        logger.info(f"Extracted {len(fields)} fields from {doc_type} document")
        
    except Exception as e:
        logger.error(f"Error parsing fields for {doc_type}: {e}")
    
    return fields, confidence

def clean_extracted_value(value: str) -> str | None:
    """
    Clean and normalize extracted field values.
    
    Args:
        value: Raw extracted value
        
    Returns:
        Cleaned value
    """
    if not value:
        return None
    
    # Remove extra whitespace and normalize
    cleaned = re.sub(r'\s+', ' ', value.strip())
    
    # Remove common artifacts
    cleaned = re.sub(r'^[^\w]*', '', cleaned)  # Remove leading non-word chars
    cleaned = re.sub(r'[^\w]*$', '', cleaned)  # Remove trailing non-word chars
    
    return cleaned if cleaned else None
