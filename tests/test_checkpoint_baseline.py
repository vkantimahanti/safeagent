from safeagent.experiments.checkpoint_baseline import (
    run_checkpoint_only_baseline,
)


def test_checkpoint_only_baseline(tmp_path):
    db_path = str(tmp_path / "checkpoint.db")

    result = run_checkpoint_only_baseline(db_path)

    assert result["ticket_count"] == 2
    assert result["retry_attempted"] is True
    assert result["checkpoint_tool_completed"] is False


from safeagent.experiments.checkpoint_baseline import (
    run_checkpoint_with_stable_id,
)


def test_checkpoint_with_stable_id(tmp_path):
    db_path = str(tmp_path / "checkpoint_stable.db")

    result = run_checkpoint_with_stable_id(db_path)

    assert result["ticket_count"] == 1
    assert result["retry_attempted"] is True
    assert result["checkpoint_tool_completed"] is False