import os
import sys

from safeagent.services.persistent_utility_service import (
    PersistentUtilityService,
)
from safeagent.agents.persistent_recovery_workflow import (
    build_persistent_recovery_workflow,
)


DB_PATH = "exp009_crash_tickets.db"
OPERATION_ID = "exp009-real-crash-001"
CUSTOMER_ID = "CUST-001"
ISSUE = "Power outage"


def crash_after_commit():
    service = PersistentUtilityService(DB_PATH)

    service.create_ticket(
        customer_id=CUSTOMER_ID,
        issue=ISSUE,
        operation_id=OPERATION_ID,
    )

    print("Ticket committed successfully", flush=True)
    print("Simulating process crash...", flush=True)

    os._exit(99)


def recover():
    workflow = build_persistent_recovery_workflow()

    result = workflow.invoke({
        "operation_type": "CREATE_TICKET",
        "operation_id": OPERATION_ID,
        "customer_id": CUSTOMER_ID,
        "issue": ISSUE,
        "db_path": DB_PATH,
    })

    print("Verification:", result["verification_status"])
    print("Recovery:", result["recovery_decision"])

    service = PersistentUtilityService(DB_PATH)
    tickets = service.list_tickets()

    print("Total tickets:", len(tickets))

    assert result["verification_status"] == "SUCCESS"
    assert result["recovery_decision"] == "STOP"
    assert len(tickets) == 1


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in {"crash", "recover"}:
        raise SystemExit(
            "Usage: python run_exp009_crash.py [crash|recover]"
        )

    if sys.argv[1] == "crash":
        crash_after_commit()
    else:
        recover()