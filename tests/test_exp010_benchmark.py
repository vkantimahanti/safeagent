from safeagent.experiments.exp010_benchmark import run_benchmark


def test_benchmark_generates_reproducible_results(tmp_path):
    path1 = tmp_path / "run1.csv"
    path2 = tmp_path / "run2.csv"

    results1 = run_benchmark(
        trials=1000,
        seed=42,
        output_path=str(path1),
    )

    results2 = run_benchmark(
        trials=1000,
        seed=42,
        output_path=str(path2),
    )

    assert results1 == results2
    assert len(results1) == 4000
    assert path1.read_text() == path2.read_text()