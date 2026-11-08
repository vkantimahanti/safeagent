from dataclasses import dataclass
from enum import Enum
from typing import Callable


class VerificationStatus(str, Enum):
    SUCCESS = "SUCCESS"
    NOT_EXECUTED = "NOT_EXECUTED"
    UNKNOWN = "UNKNOWN"


class RecoveryDecision(str, Enum):
    STOP = "STOP"
    RETRY = "RETRY"
    ESCALATE = "ESCALATE"


@dataclass(frozen=True)
class RecoveryResult:
    verification_status: VerificationStatus
    decision: RecoveryDecision
    reason: str


class VerificationRecoveryController:
    """
    Determines recovery actions based on verification evidence.

    This controller does not execute business operations.
    It returns a decision for the caller to evaluate.
    """

    def decide(
        self,
        verify: Callable[[], VerificationStatus],
    ) -> RecoveryResult:

        try:
            status = verify()
        except Exception:
            return RecoveryResult(
                verification_status=VerificationStatus.UNKNOWN,
                decision=RecoveryDecision.ESCALATE,
                reason="Verification failed; operation outcome is unknown.",
            )

        if status == VerificationStatus.SUCCESS:
            return RecoveryResult(
                verification_status=status,
                decision=RecoveryDecision.STOP,
                reason="Operation already completed successfully.",
            )

        if status == VerificationStatus.NOT_EXECUTED:
            return RecoveryResult(
                verification_status=status,
                decision=RecoveryDecision.RETRY,
                reason="Authoritative verification confirmed non-execution.",
            )

        return RecoveryResult(
            verification_status=VerificationStatus.UNKNOWN,
            decision=RecoveryDecision.ESCALATE,
            reason="Insufficient evidence to safely retry.",
        )