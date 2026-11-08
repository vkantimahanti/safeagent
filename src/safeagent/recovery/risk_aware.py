from dataclasses import dataclass
from enum import Enum

from safeagent.recovery.verification import (
    VerificationStatus,
    RecoveryDecision,
)


class OperationRisk(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass(frozen=True)
class RiskAwareRecoveryResult:
    risk: OperationRisk
    verification_status: VerificationStatus
    decision: RecoveryDecision
    reason: str


class RiskAwareRecoveryController:

    def decide(
        self,
        risk: OperationRisk,
        verification_status: VerificationStatus,
    ) -> RiskAwareRecoveryResult:

        # Operation definitely succeeded.
        if verification_status == VerificationStatus.SUCCESS:
            return RiskAwareRecoveryResult(
                risk=risk,
                verification_status=verification_status,
                decision=RecoveryDecision.STOP,
                reason="Operation already committed.",
            )

        # Outcome cannot be established.
        if verification_status == VerificationStatus.UNKNOWN:
            return RiskAwareRecoveryResult(
                risk=risk,
                verification_status=verification_status,
                decision=RecoveryDecision.ESCALATE,
                reason=(
                    "Execution outcome is unknown. "
                    "Automatic retry is unsafe."
                ),
            )

        # Authoritative evidence confirms non-execution.
        if verification_status == VerificationStatus.NOT_EXECUTED:

            if risk == OperationRisk.HIGH:
                return RiskAwareRecoveryResult(
                    risk=risk,
                    verification_status=verification_status,
                    decision=RecoveryDecision.ESCALATE,
                    reason=(
                        "High-risk operation requires "
                        "additional authorization before retry."
                    ),
                )

            return RiskAwareRecoveryResult(
                risk=risk,
                verification_status=verification_status,
                decision=RecoveryDecision.RETRY,
                reason=(
                    "Non-execution confirmed. "
                    "Retry permitted by risk policy."
                ),
            )

        return RiskAwareRecoveryResult(
            risk=risk,
            verification_status=verification_status,
            decision=RecoveryDecision.ESCALATE,
            reason="Unsupported verification status.",
        )