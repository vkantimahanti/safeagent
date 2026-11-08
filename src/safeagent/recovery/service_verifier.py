from safeagent.recovery.verification import VerificationStatus


class ServiceStateVerifier:
    """
    Verifies operation outcomes using the service's
    current in-memory operation registry.
    """

    def __init__(self, service):
        self.service = service

    def verify(self, operation_id: str) -> VerificationStatus:
        try:
            ticket = self.service.get_ticket_by_operation(operation_id)

            if ticket is not None:
                return VerificationStatus.SUCCESS

            return VerificationStatus.UNKNOWN

        except Exception:
            return VerificationStatus.UNKNOWN