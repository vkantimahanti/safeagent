from safeagent.faults.acknowledgment_loss import (
    AcknowledgmentLossInjector,
)
from safeagent.recovery.service_verifier import (
    ServiceStateVerifier,
)
from safeagent.recovery.verification import (
    RecoveryDecision,
    VerificationRecoveryController,
    VerificationStatus,
)
from safeagent.services.persistent_utility_service import (
    PersistentUtilityService,
)


def test_persistent_operation_lookup(tmp_path):
    service = PersistentUtilityService(str(tmp_path / "test.db"))

    created = service.create_ticket(
        "CUST-101",
        "Power outage",
        "OP-101",
    )

    recovered = service.get_ticket_by_operation("OP-101")

    assert recovered == created


def test_missing_persistent_operation_returns_unknown(tmp_path):
    service = PersistentUtilityService(str(tmp_path / "test.db"))

    verifier = ServiceStateVerifier(service)

    assert verifier.verify("OP-999") == VerificationStatus.UNKNOWN


def test_recovery_after_lost_acknowledgment(tmp_path):
    db_path = str(tmp_path / "test.db")

    service = PersistentUtilityService(db_path)
    injector = AcknowledgmentLossInjector()

    try:
        injector.execute(
            service.create_ticket,
            customer_id="CUST-101",
            issue="Power outage",
            operation_id="OP-101",
        )
    except TimeoutError:
        pass

    recovered_service = PersistentUtilityService(db_path)

    verifier = ServiceStateVerifier(recovered_service)
    controller = VerificationRecoveryController()

    result = controller.decide(
        verify=lambda: verifier.verify("OP-101")
    )

    assert result.verification_status == VerificationStatus.SUCCESS
    assert result.decision == RecoveryDecision.STOP
    assert len(recovered_service.list_tickets()) == 1