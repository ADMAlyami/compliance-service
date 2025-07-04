from pydantic import BaseModel
from typing import Dict, Optional

class FieldResult(BaseModel):
    value: Optional[str]
    confidence: float

class DocumentResult(BaseModel):
    file: str
    doc_type: str
    fields: Dict[str, FieldResult]
    verdict: str
