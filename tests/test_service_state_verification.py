import pytest

from safeagent.services.idempotent_utility_service import (
    IdempotentUtilityService,
)

from safeagent.faults.acknowledgment_loss import (
    AcknowledgmentLossInjector,
)

from safeagent.recovery.service_verifier import (
    ServiceStateVerifier,
)

from safeagent.recovery.verification import (
    VerificationRecoveryController,
    VerificationStatus,
    RecoveryDecision,
)


def test_existing_operation_returns_success():
    service = IdempotentUtilityService()

    service.create_ticket(
        customer_id="CUST-101",
        issue="Power outage",
        operation_id="OP-101",
    )

    verifier = ServiceStateVerifier(service)

    assert verifier.verify("OP-101") == VerificationStatus.SUCCESS


def test_missing_operation_returns_unknown():
    service = IdempotentUtilityService()

    verifier = ServiceStateVerifier(service)

    assert verifier.verify("OP-999") == VerificationStatus.UNKNOWN


def test_verification_after_acknowledgment_loss():
    service = IdempotentUtilityService()
    injector = AcknowledgmentLossInjector()

    verifier = ServiceStateVerifier(service)
    controller = VerificationRecoveryController()

    with pytest.raises(TimeoutError):
        injector.execute(
            service.create_ticket,
            customer_id="CUST-101",
            issue="Power outage",
            operation_id="OP-101",
        )

    result = controller.decide(
        verify=lambda: verifier.verify("OP-101")
    )

    assert result.verification_status == VerificationStatus.SUCCESS
    assert result.decision == RecoveryDecision.STOP
    assert len(service.list_tickets()) == 1


def test_unknown_operation_requires_escalation():
    service = IdempotentUtilityService()

    verifier = ServiceStateVerifier(service)
    controller = VerificationRecoveryController()

    result = controller.decide(
        verify=lambda: verifier.verify("OP-999")
    )

    assert result.verification_status == VerificationStatus.UNKNOWN
    assert result.decision == RecoveryDecision.ESCALATE