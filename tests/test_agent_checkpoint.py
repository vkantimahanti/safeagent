from langgraph.checkpoint.memory import MemorySaver

from safeagent.agents.workflow import build_workflow


def test_workflow_checkpoint_is_saved():
    checkpointer = MemorySaver()

    workflow = build_workflow(
        checkpointer=checkpointer
    )

    config = {
        "configurable": {
            "thread_id": "safeagent-exp009-test"
        }
    }

    result = workflow.invoke(
        {
            "operation_type": "CREATE_TICKET",
            "authorization_granted": False,
        },
        config=config,
    )

    assert result["workflow_status"] == "SIMULATED_EXECUTION"

    checkpoint = workflow.get_state(config)

    assert checkpoint.values["operation_type"] == "CREATE_TICKET"
    assert checkpoint.values["workflow_status"] == "SIMULATED_EXECUTION"
    assert checkpoint.values["recovery_decision"] == "ESCALATE"