import asyncio
import sqlite3
from contextlib import closing

import httpx

from safeagent.api.dependencies import get_service
from safeagent.api.main import app
from safeagent.faults.http_acknowledgment_loss import (
    HTTPAcknowledgmentLossTransport,
)
from safeagent.recovery.async_http_client import (
    AsyncSafeAgentHTTPRecoveryClient,
)
from safeagent.recovery.verification import RecoveryDecision
from safeagent.services.persistent_utility_service import (
    PersistentUtilityService,
)


AGENTS = 5


def test_concurrent_http_timeout_recovery(tmp_path):
    asyncio.run(run_experiment(tmp_path))


async def run_agent(agent_id, db_path, start_event):
    # Each agent gets its own HTTP client and transport.
    # This models independent client-side acknowledgment loss.
    transport = HTTPAcknowledgmentLossTransport(
        httpx.ASGITransport(app=app)
    )

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:

        recovery_client = AsyncSafeAgentHTTPRecoveryClient(client)

        payload = {
            "customer_id": "CUST-101",
            "issue": "Power outage",
            "operation_id": "OP-CONCURRENT-101",
        }

        # Release all agents at approximately the same time.
        await start_event.wait()

        try:
            await client.post("/tickets", json=payload)
            return agent_id, "SUCCESS", None

        except httpx.ReadTimeout:
            decision = await recovery_client.recover(
                "OP-CONCURRENT-101"
            )
            return agent_id, "TIMEOUT", decision


async def run_experiment(tmp_path):
    db_path = tmp_path / "concurrent_http.db"

    service = PersistentUtilityService(db_path)

    app.dependency_overrides[get_service] = lambda: service

    try:
        start_event = asyncio.Event()

        tasks = [
            asyncio.create_task(
                run_agent(agent_id, db_path, start_event)
            )
            for agent_id in range(1, AGENTS + 1)
        ]

        start_event.set()

        results = await asyncio.gather(*tasks)

        timeout_count = 0

        for agent_id, outcome, decision in results:

            print(
                f"Agent {agent_id}: "
                f"Outcome={outcome}, "
                f"Decision={decision}"
            )

            if outcome == "TIMEOUT":
                timeout_count += 1
                assert decision == RecoveryDecision.STOP

        assert timeout_count == AGENTS

        # Verify committed state independently.
        with closing(sqlite3.connect(db_path)) as conn:
            ticket_count = conn.execute(
                "SELECT COUNT(*) FROM tickets"
            ).fetchone()[0]

            operation_count = conn.execute(
                "SELECT COUNT(*) FROM operations"
            ).fetchone()[0]

        assert ticket_count == 1
        assert operation_count == 1

        print(f"Agents: {AGENTS}")
        print(f"Simulated timeouts: {timeout_count}")
        print(f"Committed tickets: {ticket_count}")
        print(f"Committed operations: {operation_count}")

    finally:
        app.dependency_overrides.clear()