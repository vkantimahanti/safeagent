from safeagent.experiments.fault_injection_benchmark import (
    run_post_commit_failure,
)


def test_post_commit_failure(tmp_path):
    result = run_post_commit_failure(
        str(tmp_path / "post_commit")
    )

    assert result["idempotent"]["tickets"] == 1
    assert result["idempotent"]["retry_attempts"] == 1

    assert result["safeagent"]["tickets"] == 1
    assert result["safeagent"]["retry_attempts"] == 0
    assert result["safeagent"]["verification"] == "SUCCESS"
    assert result["safeagent"]["decision"] == "STOP"