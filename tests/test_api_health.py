from fastapi.testclient import TestClient
from safeagent.api.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "safeagent",
    }


def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to SafeAgent API",
        "status": "running",
        "documentation": "/docs",
    }