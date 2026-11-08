import asyncio

import httpx

from safeagent.api.main import app
from safeagent.faults.http_acknowledgment_loss import (
    DelayedVerificationFailureTransport,
)


def test_delayed_transport_forwards_non_verification_requests():
    asyncio.run(run_test())


async def run_test():
    transport = DelayedVerificationFailureTransport(
        httpx.ASGITransport(app=app),
        delay_seconds=0.01,
    )

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:

        response = await client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"