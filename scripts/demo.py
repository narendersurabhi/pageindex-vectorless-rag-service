import json
from pathlib import Path

import httpx

API_URL = "http://localhost:8000"
API_KEY = "dev-key"


def upload_text(text: str) -> str:
    response = httpx.post(
        f"{API_URL}/v1/documents",
        headers={"X-API-Key": API_KEY},
        json={"text": text},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["document_id"]


def index_document(document_id: str) -> str:
    response = httpx.post(
        f"{API_URL}/v1/documents/{document_id}/index",
        headers={"X-API-Key": API_KEY},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["job_id"]


def query(document_id: str, question: str) -> dict:
    response = httpx.post(
        f"{API_URL}/v1/query",
        headers={"X-API-Key": API_KEY},
        json={"document_id": document_id, "question": question, "top_k": 2},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    sample_text = Path("sample.txt").read_text() if Path("sample.txt").exists() else "Sample text."
    doc_id = upload_text(sample_text)
    job_id = index_document(doc_id)
    print("job", job_id)
    result = query(doc_id, "What is the summary?")
    print(json.dumps(result, indent=2))
