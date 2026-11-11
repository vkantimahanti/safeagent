import sqlite3

from langgraph.checkpoint.sqlite import SqliteSaver
from safeagent.agents.workflow import build_workflow


def test_sqlite_checkpoint_persists(tmp_path):
    db_path = tmp_path / "safeagent_checkpoints.db"

    config = {
        "configurable": {
            "thread_id": "exp009-persistent-test"
        }
    }

    # First application session
    with sqlite3.connect(
            db_path,
            check_same_thread=False
        ) as conn:
        checkpointer = SqliteSaver(conn)
        workflow = build_workflow(checkpointer=checkpointer)

        result = workflow.invoke(
            {
                "operation_type": "CREATE_TICKET",
                "authorization_granted": False,
            },
            config=config,
        )

        assert result["workflow_status"] == "SIMULATED_EXECUTION"

    # Simulate application restart by reopening the database
    with sqlite3.connect(db_path) as conn:
        checkpointer = SqliteSaver(conn)
        workflow = build_workflow(checkpointer=checkpointer)

        restored = workflow.get_state(config)

        assert restored.values["operation_type"] == "CREATE_TICKET"
        assert restored.values["workflow_status"] == "SIMULATED_EXECUTION"
        assert restored.values["recovery_decision"] == "ESCALATE"