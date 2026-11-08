import pytest
from fastapi.testclient import TestClient

from safeagent.api.main import app
from safeagent.api.dependencies import get_service
from safeagent.services.persistent_utility_service import (
    PersistentUtilityService,
)


@pytest.fixture
def client(tmp_path):
    service = PersistentUtilityService(
        tmp_path / "verification_test.db"
    )

    app.dependency_overrides[get_service] = lambda: service

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


def test_existing_operation_returns_success(client):
    client.post(
        "/tickets",
        json={
            "customer_id": "CUST-101",
            "issue": "Power outage",
            "operation_id": "OP-101",
        },
    )

    response = client.get("/operations/OP-101")

    assert response.status_code == 200
    assert response.json() == {
        "operation_id": "OP-101",
        "verification_status": "SUCCESS",
        "ticket_id": "T-1",
    }


def test_missing_operation_returns_unknown(client):
    response = client.get("/operations/OP-999")

    assert response.status_code == 200
    assert response.json() == {
        "operation_id": "OP-999",
        "verification_status": "UNKNOWN",
        "ticket_id": None,
    }