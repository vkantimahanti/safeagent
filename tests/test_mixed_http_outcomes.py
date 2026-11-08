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

# Agents 1, 3, and 5 experience acknowledgment loss.
TIMEOUT_AGENTS = {1, 3, 5}


def test_mixed_http_outcomes(tmp_path):
    asyncio.run(run_experiment(tmp_path))


async def run_agent(agent_id, start_event):

    underlying_transport = httpx.ASGITransport(app=app)

    if agent_id in TIMEOUT_AGENTS:
        transport = HTTPAcknowledgmentLossTransport(
            underlying_transport
        )
    else:
        transport = underlying_transport

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:

        recovery_client = AsyncSafeAgentHTTPRecoveryClient(
            client
        )

        payload = {
            "customer_id": "CUST-101",
            "issue": "Power outage",
            "operation_id": "OP-MIXED-101",
        }

        await start_event.wait()

        try:
            response = await client.post(
                "/tickets",
                json=payload,
            )

            assert response.status_code == 201

            return {
                "agent_id": agent_id,
                "outcome": "SUCCESS",
                "ticket_id": response.json()["ticket_id"],
                "decision": None,
            }

        except httpx.ReadTimeout:

            decision = await recovery_client.recover(
                "OP-MIXED-101"
            )

            return {
                "agent_id": agent_id,
                "outcome": "TIMEOUT",
                "ticket_id": None,
                "decision": decision,
            }


async def run_experiment(tmp_path):

    db_path = tmp_path / "mixed_http.db"

    service = PersistentUtilityService(db_path)

    app.dependency_overrides[get_service] = lambda: service

    try:
        start_event = asyncio.Event()

        tasks = [
            asyncio.create_task(
                run_agent(agent_id, start_event)
            )
            for agent_id in range(1, AGENTS + 1)
        ]

        start_event.set()

        results = await asyncio.gather(*tasks)

        successful_agents = [
            result for result in results
            if result["outcome"] == "SUCCESS"
        ]

        timeout_agents = [
            result for result in results
            if result["outcome"] == "TIMEOUT"
        ]

        assert len(successful_agents) == 2
        assert len(timeout_agents) == 3

        # Both successful agents must receive the same ticket.
        successful_ticket_ids = {
            result["ticket_id"]
            for result in successful_agents
        }

        assert len(successful_ticket_ids) == 1

        # All timed-out agents must recover with STOP.
        for result in timeout_agents:
            assert result["decision"] == RecoveryDecision.STOP

        # Independently verify committed database records.
        with closing(sqlite3.connect(db_path)) as conn:

            ticket_count = conn.execute(
                "SELECT COUNT(*) FROM tickets"
            ).fetchone()[0]

            operation_count = conn.execute(
                "SELECT COUNT(*) FROM operations"
            ).fetchone()[0]

        assert ticket_count == 1
        assert operation_count == 1

        for result in results:
            print(result)

        print("\nSUMMARY")
        print(f"Agents: {AGENTS}")
        print(f"Successful responses: {len(successful_agents)}")
        print(f"Simulated timeouts: {len(timeout_agents)}")
        print(f"Committed tickets: {ticket_count}")
        print(f"Committed operations: {operation_count}")

    finally:
        app.dependency_overrides.clear()