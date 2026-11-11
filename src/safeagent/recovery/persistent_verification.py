from safeagent.services.persistent_utility_service import (
    PersistentUtilityService,
)
from safeagent.recovery.verification import VerificationStatus


def verify_persistent_ticket(
    service: PersistentUtilityService,
    operation_id: str,
    expected_customer_id: str | None = None,
    expected_issue: str | None = None,
) -> VerificationStatus:

    try:
        ticket = service.get_ticket_by_operation(operation_id)

        if ticket is None:
            return VerificationStatus.UNKNOWN

        if expected_customer_id is not None:
            if ticket.customer_id != expected_customer_id:
                return VerificationStatus.UNKNOWN

        if expected_issue is not None:
            if ticket.issue != expected_issue:
                return VerificationStatus.UNKNOWN

        return VerificationStatus.SUCCESS

    except Exception:
        return VerificationStatus.UNKNOWN