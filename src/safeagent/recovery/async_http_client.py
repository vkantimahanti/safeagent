import httpx

from safeagent.recovery.verification import (
    RecoveryDecision,
    VerificationRecoveryController,
    VerificationStatus,
)


class AsyncSafeAgentHTTPRecoveryClient:
    def __init__(self, http_client: httpx.AsyncClient):
        self.http_client = http_client
        self.controller = VerificationRecoveryController()

    async def verify_operation(
        self,
        operation_id: str,
    ) -> VerificationStatus:

        try:
            response = await self.http_client.get(
                f"/operations/{operation_id}"
            )

            response.raise_for_status()

            result = response.json()

            return VerificationStatus(
                result["verification_status"]
            )

        except (
            httpx.HTTPError,
            ValueError,
            KeyError,
            TypeError,
        ):
            return VerificationStatus.UNKNOWN

    async def recover(
        self,
        operation_id: str,
    ) -> RecoveryDecision:

        verification = await self.verify_operation(operation_id)

        result = self.controller.decide(
            lambda: verification
        )

        return result.decision