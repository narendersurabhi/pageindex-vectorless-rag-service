from fastapi.testclient import TestClient

from vectorless_rag_service.main import create_app


def test_healthz():
    client = TestClient(create_app())
    response = client.get("/healthz", headers={"X-API-Key": "dev-key"})
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
