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
)


def main():
    service = IdempotentUtilityService()
    injector = AcknowledgmentLossInjector()

    verifier = ServiceStateVerifier(service)
    controller = VerificationRecoveryController()

    operation_id = "OP-101"

    try:
        injector.execute(
            service.create_ticket,
            customer_id="CUST-101",
            issue="Power outage",
            operation_id=operation_id,
        )

    except TimeoutError:
        print("Caller observed: TimeoutError")

    result = controller.decide(
        verify=lambda: verifier.verify(operation_id)
    )

    print(f"Verification: {result.verification_status.value}")
    print(f"Decision: {result.decision.value}")
    print(f"Reason: {result.reason}")
    print(f"Total tickets: {len(service.list_tickets())}")


if __name__ == "__main__":
    main()