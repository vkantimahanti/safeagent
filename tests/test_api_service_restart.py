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


def test_recovery_after_service_reinitialization(tmp_path):

    db_path = tmp_path / "restart_recovery.db"

    # -------------------------------------------------
    # STEP 1: Create the first service instance
    # -------------------------------------------------

    service_a = PersistentUtilityService(db_path)

    app.dependency_overrides[get_service] = lambda: service_a

    payload = {
        "customer_id": "CUST-101",
        "issue": "Power outage",
        "operation_id": "OP-101",
    }

    try:
        with TestClient(app) as client:

            # Create ticket through HTTP
            response = client.post("/tickets", json=payload)

            assert response.status_code == 201
            assert response.json()["ticket_id"] == "T-1"

        # -------------------------------------------------
        # STEP 2: Replace the service instance
        # -------------------------------------------------

        service_b = PersistentUtilityService(db_path)

        assert service_b is not service_a

        app.dependency_overrides[get_service] = lambda: service_b

        # -------------------------------------------------
        # STEP 3: Verify using the new service instance
        # -------------------------------------------------

        with TestClient(app) as client:

            recovery_client = SafeAgentHTTPRecoveryClient(
                client
            )

            decision = recovery_client.recover("OP-101")

            assert decision == RecoveryDecision.STOP

            # The new service sees the original ticket.
            tickets = service_b.list_tickets()

            assert len(tickets) == 1
            assert tickets[0].ticket_id == "T-1"

    finally:
        app.dependency_overrides.clear()