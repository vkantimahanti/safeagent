import os
import sys

from safeagent.healthcare.persistent_prior_auth import (
    PersistentPriorAuthService,
)
from safeagent.recovery.risk_aware import (
    OperationRisk,
    RiskAwareRecoveryController,
)
from safeagent.recovery.verification import VerificationStatus


DB_PATH = "healthcare_crash_test.db"
OPERATION_ID = "OP-PA-CRASH-001"
MEMBER_ID = "MEMBER-001"
PROCEDURE_CODE = "PROC-123"


def crash():
    service = PersistentPriorAuthService(DB_PATH)

    record = service.submit_prior_auth(
        member_id=MEMBER_ID,
        procedure_code=PROCEDURE_CODE,
        operation_id=OPERATION_ID,
    )

    print(
        f"Committed authorization {record.authorization_id}",
        flush=True,
    )

    print("Simulating process crash...", flush=True)

    # Abrupt process termination after SQLite commit.
    os._exit(99)


def recover():
    service = PersistentPriorAuthService(DB_PATH)

    record = service.get_by_operation(OPERATION_ID)

    if (
        record is not None
        and record.member_id == MEMBER_ID
        and record.procedure_code == PROCEDURE_CODE
    ):
        verification_status = VerificationStatus.SUCCESS
    else:
        verification_status = VerificationStatus.UNKNOWN

    controller = RiskAwareRecoveryController()

    decision = controller.decide(
        risk=OperationRisk.MEDIUM,
        verification_status=verification_status,
    )

    print("Verification:", verification_status.value)
    print("Recovery decision:", decision.decision.value)
    print("Authorization count:", service.count_authorizations())


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in {"crash", "recover"}:
        raise SystemExit("Usage: python run_healthcare_crash.py crash|recover")

    if sys.argv[1] == "crash":
        crash()
    else:
        recover()