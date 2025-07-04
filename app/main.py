from fastapi import FastAPI, UploadFile, File
from app.pdf_utils import extract_text_from_pdf
from app.parser import parse_document_type, parse_fields
from app.validator import validate_fields
from app.models import DocumentResult, FieldResult

app = FastAPI()

@app.post("/check-docs")
async def check_docs(files: list[UploadFile] = File(...)):
    results = []
    for file in files:
        content = await file.read()
        text = extract_text_from_pdf(content)
        doc_type = parse_document_type(text)
        fields, confidences = parse_fields(text, doc_type)
        verdict = validate_fields(fields, doc_type)
        fields_result = {k: FieldResult(value=v, confidence=confidences.get(k, 0.0)) for k, v in fields.items()}
        results.append(DocumentResult(
            file=file.filename,
            doc_type=doc_type,
            fields=fields_result,
            verdict=verdict
        ))
    return {"results": results}
