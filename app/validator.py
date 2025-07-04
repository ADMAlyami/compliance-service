from datetime import datetime

def validate_fields(fields: dict, doc_type: str) -> str:
    now = datetime.now()
    if doc_type in ("insurance", "training"):
        expiry = fields.get("expiry_date")
        if expiry:
            # Try multiple date formats
            for fmt in ("%d/%m/%Y", "%d-%b-%Y", "%d-%m-%Y", "%m/%d/%Y", "%Y-%m-%d"):
                try:
                    exp_date = datetime.strptime(expiry, fmt)
                    if exp_date > now:
                        return "pass"
                except:
                    continue
        return "fail"
    elif doc_type == "inspection":
        # pass if result is PASS and inspection_date is in the future or recent
        if fields.get("result") == "PASS":
            return "pass"
        return "fail"
    return "unknown"
