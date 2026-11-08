import httpx
import pytest

from fastapi.testclient import TestClient

from safeagent.api.dependencies import get_service
from safeagent.api.main import app

from safeagent.recovery.http_client import (
    SafeAgentHTTPRecoveryClient,
)

from safeagent.recovery.verification import RecoveryDecision

from safeagent.services.persistent_utility_service import (
    PersistentUtilityService,
)


@pytest.fixture
def recovery_environment(tmp_path):
    service = PersistentUtilityService(
        tmp_path / "http_recovery.db"
    )

    app.dependency_overrides[get_service] = lambda: service

    try:
        with TestClient(app) as client:
            yield client, service
    finally:
        app.dependency_overrides.clear()


def test_recovery_stops_after_verified_success(recovery_environment):
    client, service = recovery_environment

    payload = {
        "customer_id": "CUST-101",
        "issue": "Power outage",
        "operation_id": "OP-101",
    }

    # The HTTP operation commits successfully.
    response = client.post("/tickets", json=payload)
    assert response.status_code == 201

    # Simulate lost acknowledgment: the recovery logic
    # does not use the POST response.
    recovery_client = SafeAgentHTTPRecoveryClient(client)

    decision = recovery_client.recover("OP-101")

    assert decision == RecoveryDecision.STOP
    assert len(service.list_tickets()) == 1


def test_recovery_escalates_unknown_operation(recovery_environment):
    client, service = recovery_environment

    recovery_client = SafeAgentHTTPRecoveryClient(client)

    decision = recovery_client.recover("OP-999")

    assert decision == RecoveryDecision.ESCALATE
    assert len(service.list_tickets()) == 0