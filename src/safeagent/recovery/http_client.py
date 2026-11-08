import httpx

from safeagent.recovery.verification import (
    RecoveryDecision,
    VerificationRecoveryController,
    VerificationStatus,
)


class SafeAgentHTTPRecoveryClient:
    def __init__(self, http_client: httpx.Client):
        self.http_client = http_client
        self.controller = VerificationRecoveryController()

    def verify_operation(self, operation_id: str) -> VerificationStatus:
        try:
            response = self.http_client.get(
                f"/operations/{operation_id}"
            )
            response.raise_for_status()

            result = response.json()
            return VerificationStatus(result["verification_status"])

        except (
            httpx.HTTPError,
            ValueError,
            KeyError,
        ):
            return VerificationStatus.UNKNOWN


    def recover(self, operation_id: str) -> RecoveryDecision:
        result = self.controller.decide(
            lambda: self.verify_operation(operation_id)
        )

        return result.decision