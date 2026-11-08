from safeagent.recovery.verification import (
    VerificationRecoveryController,
    VerificationStatus,
    RecoveryDecision,
)


def test_successful_operation_does_not_retry():
    controller = VerificationRecoveryController()

    result = controller.decide(
        verify=lambda: VerificationStatus.SUCCESS
    )

    assert result.decision == RecoveryDecision.STOP


def test_confirmed_non_execution_allows_retry_decision():
    controller = VerificationRecoveryController()

    result = controller.decide(
        verify=lambda: VerificationStatus.NOT_EXECUTED
    )

    assert result.decision == RecoveryDecision.RETRY


def test_unknown_outcome_requires_escalation():
    controller = VerificationRecoveryController()

    result = controller.decide(
        verify=lambda: VerificationStatus.UNKNOWN
    )

    assert result.decision == RecoveryDecision.ESCALATE


def test_verification_timeout_requires_escalation():
    controller = VerificationRecoveryController()

    def failing_verifier():
        raise TimeoutError("Verification service unavailable")

    result = controller.decide(
        verify=failing_verifier
    )

    assert result.verification_status == VerificationStatus.UNKNOWN
    assert result.decision == RecoveryDecision.ESCALATE


def test_unrecognized_verification_status_requires_escalation():
    controller = VerificationRecoveryController()

    result = controller.decide(
        verify=lambda: "INVALID_STATUS"
    )

    assert result.verification_status == VerificationStatus.UNKNOWN
    assert result.decision == RecoveryDecision.ESCALATE