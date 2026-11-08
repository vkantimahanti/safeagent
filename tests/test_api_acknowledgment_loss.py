import pytest
from fastapi.testclient import TestClient

from safeagent.api.dependencies import get_service
from safeagent.api.main import app
from safeagent.services.persistent_utility_service import (
    PersistentUtilityService,
)


@pytest.fixture
def client_and_service(tmp_path):
    service = PersistentUtilityService(
        tmp_path / "acknowledgment_loss.db"
    )

    app.dependency_overrides[get_service] = lambda: service

    try:
        with TestClient(app) as client:
            yield client, service
    finally:
        app.dependency_overrides.clear()


def test_http_acknowledgment_loss_recovery(client_and_service):
    client, service = client_and_service

    payload = {
        "customer_id": "CUST-101",
        "issue": "Power outage",
        "operation_id": "OP-101",
    }

    # Step 1: Server processes and commits the HTTP request.
    response = client.post("/tickets", json=payload)

    assert response.status_code == 201

    # Step 2: Simulate acknowledgment loss by withholding
    # the response from the recovery decision.
    #
    # This is a controlled client-side simulation.
    # TestClient itself successfully received the response.

    # Step 3: Verify the operation through the HTTP API.
    verification = client.get("/operations/OP-101")

    assert verification.status_code == 200
    assert verification.json()["verification_status"] == "SUCCESS"

    # Step 4: Confirm that only one ticket exists.
    assert len(service.list_tickets()) == 1


def test_http_retry_after_lost_acknowledgment(client_and_service):
    client, service = client_and_service

    payload = {
        "customer_id": "CUST-101",
        "issue": "Power outage",
        "operation_id": "OP-101",
    }

    # Initial request succeeds.
    first = client.post("/tickets", json=payload)

    assert first.status_code == 201

    # Simulate a caller that did not receive the first response.
    # The caller retries the same logical operation.
    retry = client.post("/tickets", json=payload)

    assert retry.status_code == 201

    # The retry must return the original ticket.
    assert retry.json()["ticket_id"] == first.json()["ticket_id"]

    # Only one business record must exist.
    assert len(service.list_tickets()) == 1