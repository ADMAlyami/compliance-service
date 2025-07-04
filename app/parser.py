import re
from typing import Dict, Tuple

def parse_document_type(text: str) -> str:
    text_lower = text.lower()
    if "liability insurance" in text_lower:
        return "insurance"
    if "inspection checklist" in text_lower or "inspection sheet" in text_lower:
        return "inspection"
    if "training card" in text_lower or "osha" in text_lower:
        return "training"
    return "unknown"

def parse_fields(text: str, doc_type: str) -> Tuple[Dict[str, str], Dict[str, float]]:
    fields = {}
    confidence = {}

    if doc_type == "insurance":
        insured = re.search(r"INSURED: (.+)", text)
        policy = re.search(r"POLICY NUMBER: (.+)", text)
        insurer = re.search(r"INSURER: (.+)", text)
        coverage = re.search(r"COVERAGE TYPE: (.+)", text)
        issue = re.search(r"EFFECTIVE DATE: ([\d/-]+)", text)
        expiry = re.search(r"EXPIR(Y|I) DATE: ([\d/-]+)", text, re.IGNORECASE)
        fields["insured"] = insured.group(1).strip() if insured else None
        confidence["insured"] = 0.95 if insured else 0.0
        fields["policy_number"] = policy.group(1).strip() if policy else None
        confidence["policy_number"] = 0.95 if policy else 0.0
        fields["insurer"] = insurer.group(1).strip() if insurer else None
        confidence["insurer"] = 0.95 if insurer else 0.0
        fields["coverage_type"] = coverage.group(1).strip() if coverage else None
        confidence["coverage_type"] = 0.9 if coverage else 0.0
        fields["effective_date"] = issue.group(1).strip() if issue else None
        confidence["effective_date"] = 0.95 if issue else 0.0
        fields["expiry_date"] = expiry.group(2).strip() if expiry else None
        confidence["expiry_date"] = 0.95 if expiry else 0.0

    elif doc_type == "inspection":
        inspector = re.search(r"Inspector: (.+)", text)
        inspection_date = re.search(r"Inspection Date: (.+)", text)
        equipment_id = re.search(r"(Crane|Equipment) ID: (.+)", text)
        result = re.search(r"Result: (PASS|FAIL)", text, re.IGNORECASE)
        fields["inspector"] = inspector.group(1).strip() if inspector else None
        confidence["inspector"] = 0.95 if inspector else 0.0
        fields["inspection_date"] = inspection_date.group(1).strip() if inspection_date else None
        confidence["inspection_date"] = 0.95 if inspection_date else 0.0
        fields["equipment_id"] = equipment_id.group(2).strip() if equipment_id else None
        confidence["equipment_id"] = 0.9 if equipment_id else 0.0
        fields["result"] = result.group(1).strip().upper() if result else None
        confidence["result"] = 0.95 if result else 0.0

    elif doc_type == "training":
        name = re.search(r"Worker Name: (.+)", text)
        cert_id = re.search(r"Certificate ID: (.+)", text)
        hours = re.search(r"Hours: (.+)", text)
        issue = re.search(r"Issue Date: (.+)", text)
        expiry = re.search(r"Expiry Date: (.+)", text)
        issued_by = re.search(r"Issued By: (.+)", text)
        fields["worker_name"] = name.group(1).strip() if name else None
        confidence["worker_name"] = 0.95 if name else 0.0
        fields["certificate_id"] = cert_id.group(1).strip() if cert_id else None
        confidence["certificate_id"] = 0.95 if cert_id else 0.0
        fields["hours"] = hours.group(1).strip() if hours else None
        confidence["hours"] = 0.9 if hours else 0.0
        fields["issue_date"] = issue.group(1).strip() if issue else None
        confidence["issue_date"] = 0.95 if issue else 0.0
        fields["expiry_date"] = expiry.group(1).strip() if expiry else None
        confidence["expiry_date"] = 0.95 if expiry else 0.0
        fields["issued_by"] = issued_by.group(1).strip() if issued_by else None
        confidence["issued_by"] = 0.95 if issued_by else 0.0

    else:
        # fallback, extract nothing
        pass

    return fields, confidence
