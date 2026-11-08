from pathlib import Path
from tempfile import TemporaryDirectory

from safeagent.faults.acknowledgment_loss import (
    AcknowledgmentLossInjector,
)
from safeagent.recovery.service_verifier import (
    ServiceStateVerifier,
)
from safeagent.recovery.verification import (
    VerificationRecoveryController,
)
from safeagent.services.persistent_utility_service import (
    PersistentUtilityService,
)


def run_experiment():
    with TemporaryDirectory() as directory:
        db_path = str(Path(directory) / "safeagent.db")

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
            print("Caller observed: TimeoutError")

        # Simulate a new service instance after the lost response.
        recovered_service = PersistentUtilityService(db_path)

        verifier = ServiceStateVerifier(recovered_service)
        controller = VerificationRecoveryController()

        result = controller.decide(
            verify=lambda: verifier.verify("OP-101")
        )

        print("Verification:", result.verification_status.value)
        print("Decision:", result.decision.value)
        print("Reason:", result.reason)
        print("Total tickets:", len(recovered_service.list_tickets()))


if __name__ == "__main__":
    run_experiment()