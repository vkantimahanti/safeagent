import pytest

from safeagent.healthcare.persistent_prior_auth import (
    PersistentPriorAuthService,
)


def test_authorization_survives_restart(tmp_path):
    db_path = str(tmp_path / "prior_auth.db")

    first_service = PersistentPriorAuthService(db_path)

    first = first_service.submit_prior_auth(
        member_id="MEMBER-001",
        procedure_code="PROC-123",
        operation_id="OP-001",
    )

    # Simulate application restart with a new service instance.
    restarted_service = PersistentPriorAuthService(db_path)

    recovered = restarted_service.get_by_operation("OP-001")

    assert recovered is not None
    assert recovered.authorization_id == first.authorization_id
    assert restarted_service.count_authorizations() == 1


def test_idempotency_survives_restart(tmp_path):
    db_path = str(tmp_path / "prior_auth.db")

    first_service = PersistentPriorAuthService(db_path)

    first = first_service.submit_prior_auth(
        member_id="MEMBER-001",
        procedure_code="PROC-123",
        operation_id="OP-001",
    )

    restarted_service = PersistentPriorAuthService(db_path)

    second = restarted_service.submit_prior_auth(
        member_id="MEMBER-001",
        procedure_code="PROC-123",
        operation_id="OP-001",
    )

    assert first.authorization_id == second.authorization_id
    assert restarted_service.count_authorizations() == 1


def test_operation_id_payload_mismatch(tmp_path):
    db_path = str(tmp_path / "prior_auth.db")

    service = PersistentPriorAuthService(db_path)

    service.submit_prior_auth(
        member_id="MEMBER-001",
        procedure_code="PROC-123",
        operation_id="OP-001",
    )

    with pytest.raises(ValueError):
        service.submit_prior_auth(
            member_id="MEMBER-002",
            procedure_code="PROC-123",
            operation_id="OP-001",
        )

    assert service.count_authorizations() == 1