import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
import re

logger = logging.getLogger(__name__)

# Common date formats - expanded to handle more variations
DATE_FORMATS = [
    "%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%m-%d-%Y",
    "%d/%m/%y", "%m/%d/%y", "%y-%m-%d", "%d-%m-%y", "%m-%d-%y",
    "%B %d, %Y", "%d %B %Y", "%Y %B %d",
    "%b %d, %Y", "%d %b %Y", "%Y %b %d",
    # Add formats for dates like "15-May-2030"
    "%d-%b-%Y", "%d-%B-%Y",
    "%Y-%b-%d", "%Y-%B-%d",
    "%b %d %Y", "%B %d %Y",
    "%d %b %Y", "%d %B %Y"
]

def parse_date(date_string: str) -> Optional[datetime]:
    """
    Parse date string using multiple formats.
    
    Args:
        date_string: Date string to parse
        
    Returns:
        Parsed datetime object or None if parsing fails
    """
    if not date_string:
        return None
    
    # Clean the date string
    date_string = date_string.strip()
    
    # Skip obviously invalid dates
    if len(date_string) < 3 or date_string.lower() in ['n/a', 'none', 'unknown', 'tbd', 'y']:
        logger.warning(f"Skipping invalid date: {date_string}")
        return None
    
    # Try to parse with different formats
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    
    # Try to extract date from more complex strings
    try:
        # Look for date patterns in text
        date_patterns = [
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
            r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',
            # Pattern for "15-May-2030" format
            r'(\d{1,2})-([A-Za-z]{3,})-(\d{4})',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, date_string)
            if match:
                groups = match.groups()
                if len(groups) == 3:
                    if pattern == r'(\d{1,2})-([A-Za-z]{3,})-(\d{4})':
                        # Handle "15-May-2030" format
                        day, month, year = groups
                        try:
                            # Try to parse month name
                            month_num = datetime.strptime(month, "%b").month
                            return datetime(int(year), month_num, int(day))
                        except ValueError:
                            try:
                                month_num = datetime.strptime(month, "%B").month
                                return datetime(int(year), month_num, int(day))
                            except ValueError:
                                continue
                    else:
                        # Handle numeric formats
                        day, month, year = groups
                        # Handle 2-digit years
                        if len(year) == 2:
                            year = f"20{year}" if int(year) < 50 else f"19{year}"
                        return datetime(int(year), int(month), int(day))
    except Exception as e:
        logger.debug(f"Error parsing date '{date_string}': {e}")
    
    logger.warning(f"Could not parse date: {date_string}")
    return None

def validate_insurance_document(fields: Dict[str, str]) -> str:
    """
    Validate insurance document fields.
    
    Args:
        fields: Extracted fields from insurance document
        
    Returns:
        Validation result: "pass", "fail", or "unknown"
    """
    try:
        # Check for required fields
        required_fields = ["insured", "policy_number"]
        missing_fields = [field for field in required_fields if not fields.get(field)]
        
        if missing_fields:
            logger.info(f"Insurance document missing required fields: {missing_fields}")
            return "fail"
        
        # Check expiry date
        expiry_date = fields.get("expiry_date")
        if expiry_date:
            parsed_expiry = parse_date(expiry_date)
            if parsed_expiry:
                now = datetime.now()
                # Allow 30-day grace period
                if parsed_expiry > now - timedelta(days=30):
                    logger.info("Insurance document has valid expiry date")
                    return "pass"
                else:
                    logger.info("Insurance document has expired")
                    return "fail"
        
        # If no valid expiry date, but we have required fields, give benefit of doubt
        if fields.get("insured") and fields.get("policy_number"):
            logger.info("Insurance document has required fields but no valid expiry date")
            return "unknown"
        
        return "fail"
        
    except Exception as e:
        logger.error(f"Error validating insurance document: {e}")
        return "unknown"

def validate_inspection_document(fields: Dict[str, str]) -> str:
    """
    Validate inspection document fields.
    
    Args:
        fields: Extracted fields from inspection document
        
    Returns:
        Validation result: "pass", "fail", or "unknown"
    """
    try:
        # Check for required fields
        required_fields = ["inspector", "inspection_date"]
        missing_fields = [field for field in required_fields if not fields.get(field)]
        
        if missing_fields:
            logger.info(f"Inspection document missing required fields: {missing_fields}")
            return "fail"
        
        # Check inspection result
        result = fields.get("result", "").upper()
        if result == "PASS":
            # Check if inspection is recent (within last year)
            inspection_date = fields.get("inspection_date")
            if inspection_date:
                parsed_date = parse_date(inspection_date)
                if parsed_date:
                    now = datetime.now()
                    if parsed_date > now - timedelta(days=365):
                        logger.info("Inspection document is recent and passed")
                        return "pass"
                    else:
                        logger.info("Inspection document is too old")
                        return "fail"
            
            logger.info("Inspection document passed but date unclear")
            return "pass"
        elif result == "FAIL":
            logger.info("Inspection document failed")
            return "fail"
        else:
            logger.info("Inspection document result unclear")
            return "unknown"
        
    except Exception as e:
        logger.error(f"Error validating inspection document: {e}")
        return "unknown"

def validate_training_document(fields: Dict[str, str]) -> str:
    """
    Validate training document fields.
    
    Args:
        fields: Extracted fields from training document
        
    Returns:
        Validation result: "pass", "fail", or "unknown"
    """
    try:
        # Check for required fields
        required_fields = ["worker_name", "certificate_id"]
        missing_fields = [field for field in required_fields if not fields.get(field)]
        
        if missing_fields:
            logger.info(f"Training document missing required fields: {missing_fields}")
            return "fail"
        
        # Check expiry date
        expiry_date = fields.get("expiry_date")
        if expiry_date:
            parsed_expiry = parse_date(expiry_date)
            if parsed_expiry:
                now = datetime.now()
                # Allow 30-day grace period
                if parsed_expiry > now - timedelta(days=30):
                    logger.info("Training document has valid expiry date")
                    return "pass"
                else:
                    logger.info("Training document has expired")
                    return "fail"
        
        # If no valid expiry date, but we have required fields, give benefit of doubt
        if fields.get("worker_name") and fields.get("certificate_id"):
            logger.info("Training document has required fields but no valid expiry date")
            return "unknown"
        
        return "fail"
        
    except Exception as e:
        logger.error(f"Error validating training document: {e}")
        return "unknown"

def validate_fields(fields: Dict[str, str], doc_type: str) -> str:
    """
    Validate document fields based on document type.
    
    Args:
        fields: Extracted fields from document
        doc_type: Type of document
        
    Returns:
        Validation result: "pass", "fail", or "unknown"
    """
    try:
        logger.info(f"Validating {doc_type} document with {len(fields)} fields")
        
        if doc_type == "insurance":
            return validate_insurance_document(fields)
        elif doc_type == "inspection":
            return validate_inspection_document(fields)
        elif doc_type == "training":
            return validate_training_document(fields)
        else:
            logger.warning(f"Unknown document type for validation: {doc_type}")
            return "unknown"
            
    except Exception as e:
        logger.error(f"Error in field validation: {e}")
        return "unknown"

def get_validation_details(fields: Dict[str, str], doc_type: str) -> Dict[str, list]:
    """
    Get detailed validation information.
    
    Args:
        fields: Extracted fields from document
        doc_type: Type of document
        
    Returns:
        Dictionary with validation details
    """
    details = {
        "missing_fields": [],
        "expired_fields": [],
        "warnings": []
    }
    
    try:
        if doc_type == "insurance":
            required = ["insured", "policy_number"]
            expiry_field = "expiry_date"
        elif doc_type == "inspection":
            required = ["inspector", "inspection_date"]
            expiry_field = "inspection_date"
        elif doc_type == "training":
            required = ["worker_name", "certificate_id"]
            expiry_field = "expiry_date"
        else:
            return details
        
        # Check missing required fields
        for field in required:
            if not fields.get(field):
                details["missing_fields"].append(field)
        
        # Check expiry dates
        if expiry_field in fields and fields[expiry_field]:
            parsed_date = parse_date(fields[expiry_field])
            if parsed_date and parsed_date < datetime.now():
                details["expired_fields"].append(expiry_field)
        
        # Add warnings
        if len(details["missing_fields"]) > 0:
            details["warnings"].append(f"Missing required fields: {', '.join(details['missing_fields'])}")
        
        if len(details["expired_fields"]) > 0:
            details["warnings"].append(f"Expired fields: {', '.join(details['expired_fields'])}")
        
    except Exception as e:
        logger.error(f"Error getting validation details: {e}")
        details["warnings"].append(f"Error during validation: {str(e)}")
    
    return details
