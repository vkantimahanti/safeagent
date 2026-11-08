import multiprocessing
from pathlib import Path

from safeagent.services.persistent_utility_service import (
    PersistentUtilityService,
)
from safeagent.recovery.service_verifier import ServiceStateVerifier
from safeagent.recovery.verification import (
    RecoveryDecision,
    VerificationRecoveryController,
)


def create_operation_in_process(db_path: str, result_queue):
    """Runs in Process A."""

    service = PersistentUtilityService(Path(db_path))

    ticket = service.create_ticket(
        customer_id="CUST-101",
        issue="Power outage",
        operation_id="OP-101",
    )

    result_queue.put(ticket.ticket_id)


def verify_operation_in_process(db_path: str, result_queue):
    """Runs in Process B."""

    service = PersistentUtilityService(Path(db_path))

    verifier = ServiceStateVerifier(service)
    controller = VerificationRecoveryController()

    result = controller.decide(
        lambda: verifier.verify("OP-101")
    )

    result_queue.put(result.decision.value)


def test_recovery_across_independent_processes(tmp_path):

    db_path = str(tmp_path / "process_restart.db")

    # Use spawn to ensure each child starts a fresh interpreter.
    ctx = multiprocessing.get_context("spawn")

    # Process A creates and commits the ticket.
    queue_a = ctx.Queue()

    process_a = ctx.Process(
        target=create_operation_in_process,
        args=(db_path, queue_a),
    )

    process_a.start()
    process_a.join(timeout=15)

    assert process_a.exitcode == 0

    ticket_id = queue_a.get(timeout=5)

    assert ticket_id == "T-1"

    # Process B starts only after Process A has exited.
    queue_b = ctx.Queue()

    process_b = ctx.Process(
        target=verify_operation_in_process,
        args=(db_path, queue_b),
    )

    process_b.start()
    process_b.join(timeout=15)

    assert process_b.exitcode == 0

    decision = queue_b.get(timeout=5)

    assert decision == RecoveryDecision.STOP.value

    # Parent process independently checks the database.
    service = PersistentUtilityService(Path(db_path))

    tickets = service.list_tickets()

    assert len(tickets) == 1
    assert tickets[0].ticket_id == "T-1"