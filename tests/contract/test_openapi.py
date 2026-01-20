from fastapi.testclient import TestClient

from vectorless_rag_service.main import create_app


def test_openapi_has_paths():
    client = TestClient(create_app())
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "/v1/documents" in data["paths"]
    assert "/v1/query" in data["paths"]
