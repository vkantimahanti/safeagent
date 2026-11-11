from safeagent.experiments.comparative_benchmark import (
    run_comparative_benchmark,
)


def test_comparative_benchmark(tmp_path):
    db_path = str(tmp_path / "exp010.db")

    results = run_comparative_benchmark(db_path)

    assert results["naive"] == 2
    assert results["idempotent"] == 1
    assert results["safeagent"] == 1
    assert results["safeagent_verification"] == "SUCCESS"
    assert results["safeagent_decision"] == "STOP"