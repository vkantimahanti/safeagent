from experiments.recovery.concurrent_idempotency import (
    UnsafeTicketService,
    SafeTicketService,
    run_experiment,
)


def test_concurrent_requests_without_lock_create_duplicates():
    service = UnsafeTicketService()

    results, tickets = run_experiment(service)

    assert len(results) == 2
    assert len(tickets) == 2
    assert len(set(tickets)) == 2


def test_concurrent_requests_with_lock_prevent_duplicates():
    service = SafeTicketService()

    results, tickets = run_experiment(service)

    assert len(results) == 2
    assert len(tickets) == 1
    assert results == ["T-1001", "T-1001"]