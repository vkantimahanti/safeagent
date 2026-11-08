import asyncio

import httpx

from safeagent.api.dependencies import get_service
from safeagent.api.main import app
from safeagent.faults.http_acknowledgment_loss import (
    HTTPAcknowledgmentLossTransport,
)
from safeagent.services.persistent_utility_service import (
    PersistentUtilityService,
)

from safeagent.recovery.async_http_client import (
    AsyncSafeAgentHTTPRecoveryClient,
)
from safeagent.recovery.verification import RecoveryDecision

def test_http_timeout_after_database_commit(tmp_path):
    asyncio.run(run_experiment(tmp_path))


async def run_experiment(tmp_path):
    service = PersistentUtilityService(
        tmp_path / "transport_failure.db"
    )

    app.dependency_overrides[get_service] = lambda: service

    try:
        underlying_transport = httpx.ASGITransport(app=app)

        fault_transport = HTTPAcknowledgmentLossTransport(
            underlying_transport
        )

        async with httpx.AsyncClient(
            transport=fault_transport,
            base_url="http://testserver",
        ) as client:

            payload = {
                "customer_id": "CUST-101",
                "issue": "Power outage",
                "operation_id": "OP-101",
            }

            # First POST reaches FastAPI and commits.
            # The transport then injects a timeout.
            try:
                await client.post("/tickets", json=payload)

                assert False, "Expected an injected timeout"

            except httpx.ReadTimeout:
                pass

            # Verify that the ticket was committed.
            assert len(service.list_tickets()) == 1

            # Verify through HTTP.
            verification = await client.get(
                "/operations/OP-101"
            )

            assert verification.status_code == 200
            assert (
                verification.json()["verification_status"]
                == "SUCCESS"
            )

            # Confirm no duplicate was created.
            assert len(service.list_tickets()) == 1

    finally:
        app.dependency_overrides.clear()


def test_timeout_triggers_verified_stop_decision(tmp_path):
    asyncio.run(run_recovery_experiment(tmp_path))


async def run_recovery_experiment(tmp_path):
    service = PersistentUtilityService(
        tmp_path / "recovery_decision.db"
    )

    app.dependency_overrides[get_service] = lambda: service

    try:
        underlying_transport = httpx.ASGITransport(app=app)

        fault_transport = HTTPAcknowledgmentLossTransport(
            underlying_transport
        )

        async with httpx.AsyncClient(
            transport=fault_transport,
            base_url="http://testserver",
        ) as client:

            recovery_client = AsyncSafeAgentHTTPRecoveryClient(
                client
            )

            payload = {
                "customer_id": "CUST-101",
                "issue": "Power outage",
                "operation_id": "OP-101",
            }

            timeout_occurred = False

            try:
                await client.post("/tickets", json=payload)

            except httpx.ReadTimeout:
                timeout_occurred = True

            assert timeout_occurred is True

            # The operation was committed before timeout injection.
            assert len(service.list_tickets()) == 1

            # Recovery client queries HTTP and applies
            # the centralized recovery policy.
            decision = await recovery_client.recover("OP-101")

            assert decision == RecoveryDecision.STOP

            # No duplicate business effect.
            assert len(service.list_tickets()) == 1

    finally:
        app.dependency_overrides.clear()