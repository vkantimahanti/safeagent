import asyncio

import httpx

from safeagent.api.dependencies import get_service
from safeagent.api.main import app

from safeagent.faults.http_acknowledgment_loss import (
    HTTPAcknowledgmentLossTransport,
    HTTPVerificationFailureTransport,
)

from safeagent.recovery.async_http_client import (
    AsyncSafeAgentHTTPRecoveryClient,
)

from safeagent.recovery.verification import RecoveryDecision

from safeagent.services.persistent_utility_service import (
    PersistentUtilityService,
)


def test_verification_timeout_requires_escalation(tmp_path):
    asyncio.run(run_experiment(tmp_path))


async def run_experiment(tmp_path):
    service = PersistentUtilityService(
        tmp_path / "verification_failure.db"
    )

    app.dependency_overrides[get_service] = lambda: service

    try:
        # FastAPI receives requests through ASGITransport.
        underlying_transport = httpx.ASGITransport(app=app)

        # First wrapper: fail verification requests.
        verification_failure_transport = (
            HTTPVerificationFailureTransport(
                underlying_transport
            )
        )

        # Second wrapper: lose the first POST acknowledgment.
        fault_transport = HTTPAcknowledgmentLossTransport(
            verification_failure_transport
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

            # The server commits the operation, but the
            # transport injects a timeout afterward.
            try:
                await client.post("/tickets", json=payload)

                assert False, "Expected POST acknowledgment timeout"

            except httpx.ReadTimeout:
                pass

            # Confirm the business operation completed.
            assert len(service.list_tickets()) == 1

            # Verification also experiences a timeout.
            decision = await recovery_client.recover("OP-101")

            # The controller must choose ESCALATE.
            assert decision == RecoveryDecision.ESCALATE

            # No additional ticket should be created.
            assert len(service.list_tickets()) == 1

    finally:
        app.dependency_overrides.clear()