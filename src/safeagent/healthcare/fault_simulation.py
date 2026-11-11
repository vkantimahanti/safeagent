from safeagent.healthcare.prior_auth_service import PriorAuthService
from safeagent.recovery.risk_aware import (
    OperationRisk,
    RiskAwareRecoveryController,
)
from safeagent.recovery.verification import VerificationStatus

def simulate_lost_acknowledgment():
    service = PriorAuthService()

    member_id = "MEMBER-001"
    procedure_code = "PROC-123"

    # First request succeeds at the payer.
    service.submit_prior_auth(
        member_id=member_id,
        procedure_code=procedure_code,
    )

    # Simulate the agent losing the success acknowledgment.
    acknowledgment_received = False

    retries = 0

    # Naive agent retries without checking the payer.
    if not acknowledgment_received:
        retries += 1

        service.submit_prior_auth(
            member_id=member_id,
            procedure_code=procedure_code,
        )

    authorizations = service.list_authorizations()

    return {
        "approach": "naive",
        "total_authorizations": len(authorizations),
        "retries": retries,
        "duplicate_submissions": max(0, len(authorizations) - 1),
    }



def simulate_idempotent_lost_acknowledgment():
    service = PriorAuthService()

    member_id = "MEMBER-001"
    procedure_code = "PROC-123"
    operation_id = "OP-PA-001"

    # First submission succeeds, but the acknowledgment is lost.
    service.submit_prior_auth(
        member_id=member_id,
        procedure_code=procedure_code,
        operation_id=operation_id,
    )

    retries = 1

    # Retry with the SAME operation ID.
    service.submit_prior_auth(
        member_id=member_id,
        procedure_code=procedure_code,
        operation_id=operation_id,
    )

    authorizations = service.list_authorizations()

    return {
        "approach": "idempotent",
        "total_authorizations": len(authorizations),
        "retries": retries,
        "duplicate_submissions": max(0, len(authorizations) - 1),
    }



def simulate_safeagent_lost_acknowledgment():
    service = PriorAuthService()

    member_id = "MEMBER-001"
    procedure_code = "PROC-123"
    operation_id = "OP-PA-001"

    # Payer commits the submission.
    service.submit_prior_auth(
        member_id=member_id,
        procedure_code=procedure_code,
        operation_id=operation_id,
    )

    # Agent loses acknowledgment and verifies the outcome.
    existing = service.get_authorization_by_operation(operation_id)

    if (
        existing is not None
        and existing.member_id == member_id
        and existing.procedure_code == procedure_code
    ):
        verification_status = VerificationStatus.SUCCESS
    else:
        # Missing evidence does not prove non-execution.
        verification_status = VerificationStatus.UNKNOWN

    controller = RiskAwareRecoveryController()

    result = controller.decide(
        risk=OperationRisk.MEDIUM,
        verification_status=verification_status,
    )

    retries = 0

    if result.decision.value == "RETRY":
        retries += 1
        service.submit_prior_auth(
            member_id=member_id,
            procedure_code=procedure_code,
            operation_id=operation_id,
        )

    authorizations = service.list_authorizations()

    return {
        "approach": "safeagent",
        "total_authorizations": len(authorizations),
        "retries": retries,
        "duplicate_submissions": max(0, len(authorizations) - 1),
        "verification_status": verification_status.value,
        "recovery_decision": result.decision.value,
    }



def simulate_safeagent_verification_outage():
    service = PriorAuthService()

    member_id = "MEMBER-001"
    procedure_code = "PROC-123"
    operation_id = "OP-PA-002"

    # Payer successfully commits the authorization.
    service.submit_prior_auth(
        member_id=member_id,
        procedure_code=procedure_code,
        operation_id=operation_id,
    )

    # Simulate verification service being unavailable.
    verification_status = VerificationStatus.UNKNOWN

    controller = RiskAwareRecoveryController()

    result = controller.decide(
        risk=OperationRisk.MEDIUM,
        verification_status=verification_status,
    )

    retries = 0

    if result.decision.value == "RETRY":
        retries += 1

        service.submit_prior_auth(
            member_id=member_id,
            procedure_code=procedure_code,
            operation_id=operation_id,
        )

    return {
        "approach": "safeagent",
        "total_authorizations": len(service.list_authorizations()),
        "retries": retries,
        "duplicate_submissions": max(
            0,
            len(service.list_authorizations()) - 1,
        ),
        "verification_status": verification_status.value,
        "recovery_decision": result.decision.value,
    }


def simulate_safeagent_confirmed_non_execution():
    service = PriorAuthService()

    member_id = "MEMBER-001"
    procedure_code = "PROC-123"
    operation_id = "OP-PA-003"

    # Simulate a request rejected before reaching the payer.
    # No submission is made to the service.
    #
    # This status comes from a trusted pre-execution rejection,
    # NOT merely from a missing database record.
    verification_status = VerificationStatus.NOT_EXECUTED

    controller = RiskAwareRecoveryController()

    result = controller.decide(
        risk=OperationRisk.MEDIUM,
        verification_status=verification_status,
    )

    retries = 0

    if result.decision.value == "RETRY":
        retries += 1

        service.submit_prior_auth(
            member_id=member_id,
            procedure_code=procedure_code,
            operation_id=operation_id,
        )

    return {
        "approach": "safeagent",
        "total_authorizations": len(service.list_authorizations()),
        "retries": retries,
        "duplicate_submissions": max(
            0,
            len(service.list_authorizations()) - 1,
        ),
        "verification_status": verification_status.value,
        "recovery_decision": result.decision.value,
    }