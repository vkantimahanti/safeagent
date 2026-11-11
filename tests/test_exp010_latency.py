from safeagent.experiments.latency_benchmark import (
    measure_recovery_latency,
)


def test_latency_benchmark(tmp_path):
    result = measure_recovery_latency(
        str(tmp_path / "latency")
    )

    assert result["idempotent_ms"] >= 0
    assert result["safeagent_ms"] >= 0
    assert result["safeagent_decision"] == "STOP"