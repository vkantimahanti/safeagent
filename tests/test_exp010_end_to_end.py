from safeagent.experiments.end_to_end_comparison import (
    run_naive_post_commit_failure,
)
from safeagent.experiments.end_to_end_comparison import (
    run_idempotent_post_commit_failure,
)
from safeagent.experiments.end_to_end_comparison import (
    run_safeagent_post_commit_failure,
)
from safeagent.experiments.end_to_end_comparison import (
    run_checkpoint_post_commit_failure,
)
from safeagent.experiments.end_to_end_comparison import (
    run_safeagent_missing_operation,
)

from unittest.mock import patch

from safeagent.services.persistent_utility_service import (
    PersistentUtilityService,
)
from safeagent.agents.persistent_recovery_workflow import (
    build_persistent_recovery_workflow,
)

def test_naive_post_commit_failure():
    result = run_naive_post_commit_failure()

    assert result["approach"] == "naive"
    assert result["ticket_count"] == 2
    assert result["recovery_retries"] == 1
    assert result["duplicate_count"] == 1


def test_idempotent_post_commit_failure(tmp_path):
    result = run_idempotent_post_commit_failure(
        str(tmp_path / "idempotent.db")
    )

    assert result["approach"] == "idempotent"
    assert result["ticket_count"] == 1
    assert result["recovery_retries"] == 1
    assert result["duplicate_count"] == 0



def test_safeagent_post_commit_failure(tmp_path):
    result = run_safeagent_post_commit_failure(
        str(tmp_path / "safeagent.db")
    )

    assert result["approach"] == "safeagent"
    assert result["ticket_count"] == 1
    assert result["duplicate_count"] == 0

    assert result["recovery_retries"] == 0
    assert result["verification_status"] == "SUCCESS"
    assert result["recovery_decision"] == "STOP"


def test_checkpoint_post_commit_failure(tmp_path):
    result = run_checkpoint_post_commit_failure(
        str(tmp_path / "checkpoint.db")
    )

    assert result["approach"] == "checkpoint_stable"
    assert result["ticket_count"] == 1
    assert result["recovery_retries"] == 1
    assert result["duplicate_count"] == 0


def test_safeagent_missing_operation(tmp_path):
    result = run_safeagent_missing_operation(
        str(tmp_path / "missing.db")
    )

    assert result["ticket_count"] == 0
    assert result["verification_status"] == "UNKNOWN"
    assert result["recovery_decision"] == "ESCALATE"



def test_safeagent_verification_outage(tmp_path):
    db_path = str(tmp_path / "verification_outage.db")

    service = PersistentUtilityService(db_path)

    operation_id = "exp010-outage-001"

    service.create_ticket(
        customer_id="MEMBER-001",
        issue="Prior authorization request",
        operation_id=operation_id,
    )

    workflow = build_persistent_recovery_workflow()

    # Simulate verification service failure.
    with patch.object(
        PersistentUtilityService,
        "get_ticket_by_operation",
        side_effect=ConnectionError("Verification unavailable"),
    ):
        result = workflow.invoke({
            "operation_type": "CREATE_TICKET",
            "operation_id": operation_id,
            "customer_id": "MEMBER-001",
            "issue": "Prior authorization request",
            "db_path": db_path,
        })

    assert result["verification_status"] == "UNKNOWN"
    assert result["recovery_decision"] == "ESCALATE"

    # Verify no duplicate ticket was created.
    assert len(service.list_tickets()) == 1