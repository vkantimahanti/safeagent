import pytest
from fastapi.testclient import TestClient

from safeagent.api.dependencies import get_service
from safeagent.api.main import app
from safeagent.services.persistent_utility_service import (
    PersistentUtilityService,
)


@pytest.fixture
def client(tmp_path):
    db_path = tmp_path / "api_test.db"

    service = PersistentUtilityService(db_path)

    app.dependency_overrides[get_service] = lambda: service

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


def test_create_ticket(client):
    response = client.post(
        "/tickets",
        json={
            "customer_id": "CUST-101",
            "issue": "Power outage",
            "operation_id": "OP-101",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["ticket_id"] == "T-1"
    assert data["customer_id"] == "CUST-101"
    assert data["status"] == "OPEN"


def test_retry_returns_original_ticket(client):
    payload = {
        "customer_id": "CUST-101",
        "issue": "Power outage",
        "operation_id": "OP-101",
    }

    first = client.post("/tickets", json=payload)
    second = client.post("/tickets", json=payload)

    assert first.status_code == 201
    assert second.status_code == 201

    assert first.json()["ticket_id"] == second.json()["ticket_id"]


def test_conflicting_operation_id_returns_409(client):
    first_payload = {
        "customer_id": "CUST-101",
        "issue": "Power outage",
        "operation_id": "OP-101",
    }

    conflicting_payload = {
        "customer_id": "CUST-102",
        "issue": "Transformer failure",
        "operation_id": "OP-101",
    }

    first = client.post("/tickets", json=first_payload)
    second = client.post("/tickets", json=conflicting_payload)

    assert first.status_code == 201
    assert second.status_code == 409


def test_missing_operation_id_returns_422(client):
    response = client.post(
        "/tickets",
        json={
            "customer_id": "CUST-101",
            "issue": "Power outage",
        },
    )

    assert response.status_code == 422