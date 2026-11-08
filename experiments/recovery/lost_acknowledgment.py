from safeagent.faults.acknowledgment_loss import (
    AcknowledgmentLossInjector,
)

from safeagent.services.utility_service import UtilityService

from safeagent.services.idempotent_utility_service import (
    IdempotentUtilityService,
)


def run_naive_recovery():
    print("\n--- Naive Recovery ---")

    service = UtilityService()
    injector = AcknowledgmentLossInjector()

    try:
        injector.execute(
            service.create_ticket,
            customer_id="CUST-101",
            issue="Power outage",
        )

    except TimeoutError:
        print("Caller observed: TimeoutError")

    # Naive retry after the simulated timeout.
    retry = injector.execute(
        service.create_ticket,
        customer_id="CUST-101",
        issue="Power outage",
    )

    print(f"Retry ticket: {retry.ticket_id}")
    print(f"Total tickets: {len(service.list_tickets())}")


def run_idempotent_recovery():
    print("\n--- Idempotent Recovery ---")

    service = IdempotentUtilityService()
    injector = AcknowledgmentLossInjector()

    try:
        injector.execute(
            service.create_ticket,
            customer_id="CUST-101",
            issue="Power outage",
            operation_id="OP-101",
        )

    except TimeoutError:
        print("Caller observed: TimeoutError")

    # Retry with the SAME operation ID.
    retry = injector.execute(
        service.create_ticket,
        customer_id="CUST-101",
        issue="Power outage",
        operation_id="OP-101",
    )

    print(f"Retry ticket: {retry.ticket_id}")
    print(f"Total tickets: {len(service.list_tickets())}")


if __name__ == "__main__":
    run_naive_recovery()
    run_idempotent_recovery()