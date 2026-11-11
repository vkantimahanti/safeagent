import tempfile
from pathlib import Path

from safeagent.healthcare.fault_simulation import (
    simulate_lost_acknowledgment,
    simulate_idempotent_lost_acknowledgment,
    simulate_safeagent_lost_acknowledgment,
)
from safeagent.healthcare.persistent_prior_auth import (
    PersistentPriorAuthService,
)
from safeagent.recovery.risk_aware import (
    OperationRisk,
    RiskAwareRecoveryController,
)
from safeagent.recovery.verification import VerificationStatus


def simulate_checkpoint_recovery(db_path):
    """
    Simulate recovery using a stale checkpoint and a stable operation ID.

    This is a checkpoint-inspired baseline, not actual LangGraph
    checkpoint restoration.
    """
    operation_id = "OP-CHECKPOINT-001"

    service = PersistentPriorAuthService(db_path)

    checkpoint = {
        "operation_id": operation_id,
        "execution_complete": False,
    }

    # Payer commits the authorization.
    service.submit_prior_auth(
        member_id="MEMBER-001",
        procedure_code="PROC-123",
        operation_id=operation_id,
    )

    # The checkpoint still indicates incomplete execution.
    retries = 0

    if not checkpoint["execution_complete"]:
        retries += 1

        service.submit_prior_auth(
            member_id="MEMBER-001",
            procedure_code="PROC-123",
            operation_id=checkpoint["operation_id"],
        )

    count = service.count_authorizations()

    return {
        "approach": "checkpoint_stable",
        "total_authorizations": count,
        "retries": retries,
        "duplicate_submissions": max(0, count - 1),
    }


def main():
    with tempfile.TemporaryDirectory() as directory:
        checkpoint_db = str(
            Path(directory) / "checkpoint.db"
        )

        results = [
            simulate_lost_acknowledgment(),
            simulate_idempotent_lost_acknowledgment(),
            simulate_checkpoint_recovery(checkpoint_db),
            simulate_safeagent_lost_acknowledgment(),
        ]

        print("\nHEALTHCARE RECOVERY COMPARISON")
        print("=" * 70)

        print(
            f"{'Approach':<22}"
            f"{'Authorizations':>16}"
            f"{'Retries':>12}"
            f"{'Duplicates':>12}"
        )

        print("-" * 70)

        for result in results:
            print(
                f"{result['approach']:<22}"
                f"{result['total_authorizations']:>16}"
                f"{result['retries']:>12}"
                f"{result['duplicate_submissions']:>12}"
            )


if __name__ == "__main__":
    main()