from safeagent.healthcare.prior_auth_service import PriorAuthService

import pytest



def test_submit_prior_authorization():

    service = PriorAuthService()

    authorization = service.submit_prior_auth(
        member_id="MEMBER-001",
        procedure_code="PROC-123",
    )

    assert authorization.authorization_id == "PA-0001"
    assert authorization.status == "SUBMITTED"

    assert len(service.list_authorizations()) == 1



def test_idempotent_prior_auth_submission():

    service = PriorAuthService()

    first = service.submit_prior_auth(
        member_id="MEMBER-001",
        procedure_code="PROC-123",
        operation_id="OP-001",
    )

    second = service.submit_prior_auth(
        member_id="MEMBER-001",
        procedure_code="PROC-123",
        operation_id="OP-001",
    )

    assert first.authorization_id == second.authorization_id
    assert len(service.list_authorizations()) == 1


def test_operation_id_payload_mismatch():

    service = PriorAuthService()

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