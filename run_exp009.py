import sys
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver
from safeagent.agents.workflow import build_workflow


DB_PATH = Path("exp009_checkpoints.db")

CONFIG = {
    "configurable": {
        "thread_id": "exp009-restart-test"
    }
}


def execute():
    with SqliteSaver.from_conn_string(str(DB_PATH)) as checkpointer:
        workflow = build_workflow(checkpointer=checkpointer)

        result = workflow.invoke(
            {
                "operation_type": "CREATE_TICKET",
                "authorization_granted": False,
            },
            config=CONFIG,
        )

        print("Workflow executed")
        print("Status:", result["workflow_status"])
        print("Recovery:", result["recovery_decision"])


def restore():
    with SqliteSaver.from_conn_string(str(DB_PATH)) as checkpointer:
        workflow = build_workflow(checkpointer=checkpointer)

        checkpoint = workflow.get_state(CONFIG)

        if not checkpoint.values:
            raise RuntimeError("No saved checkpoint found")

        print("Checkpoint restored")
        print("Operation:", checkpoint.values["operation_type"])
        print("Status:", checkpoint.values["workflow_status"])
        print("Recovery:", checkpoint.values["recovery_decision"])


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in {"execute", "restore"}:
        raise SystemExit("Usage: python run_exp009.py [execute|restore]")

    if sys.argv[1] == "execute":
        execute()
    else:
        restore()