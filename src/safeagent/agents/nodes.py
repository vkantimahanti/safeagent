from safeagent.agents.state import SafeAgentState
from safeagent.recovery.operation_registry import (
    OperationType,
    get_operation_definition,
)
from safeagent.recovery.risk_aware import (
    OperationRisk,
    RiskAwareRecoveryController,
)

from safeagent.recovery.verification import VerificationStatus
from safeagent.services.persistent_utility_service import PersistentUtilityService
from safeagent.recovery.persistent_verification import verify_persistent_ticket


def load_operation_policy(state: SafeAgentState) -> dict:
    """
    Load the trusted risk classification for an operation.
    """

    operation_type = OperationType(state["operation_type"])

    definition = get_operation_definition(operation_type)

    return {
        "risk": definition.risk.value,
        "requires_authorization": definition.requires_authorization,
    }



def check_authorization(state: SafeAgentState) -> dict:
    requires_auth = state["requires_authorization"]

    if not requires_auth:
        return {"authorized": True}

    if state.get("authorization_granted", False):
        return {"authorized": True}

    return {
        "authorized": False,
        "error": "Authorization required",
    }



def route_authorization(state: SafeAgentState) -> str:
    if state.get("authorized") is True:
        return "approved"

    return "blocked"



def approved_node(state: SafeAgentState) -> dict:
    return {
        "recovery_decision": "READY_FOR_EXECUTION"
    }


def blocked_node(state: SafeAgentState) -> dict:
    return {
        "workflow_status": "BLOCKED",
        "error": "Operation blocked by authorization policy",
    }


def execute_simulated_tool(state: SafeAgentState) -> dict:
    """
    Simulate execution without performing a real operation.
    """

    if state.get("authorized") is not True:
        return {
            "tool_executed": False,
            "error": "Execution denied",
        }

    return {
    "tool_executed": True,
    "workflow_status": "SIMULATED_EXECUTION"
}

def verify_simulated_outcome(state: SafeAgentState) -> dict:
    """
    Simulate verification of an operation's execution outcome.
    """

    if state.get("tool_executed") is not True:
        return {
            "verification_status": "UNKNOWN"
        }

    status = state.get(
        "simulated_verification_status",
        "UNKNOWN"
    )

    if status not in {
        "SUCCESS",
        "NOT_EXECUTED",
        "UNKNOWN",
    }:
        status = "UNKNOWN"

    return {
        "verification_status": status
    }



def apply_recovery_policy(state: SafeAgentState) -> dict:
    """
    Apply SafeAgent's existing deterministic recovery policy.
    """

    risk = OperationRisk(state["risk"])

    verification_status = VerificationStatus(
        state["verification_status"]
    )

    controller = RiskAwareRecoveryController()

    result = controller.decide(
        risk=risk,
        verification_status=verification_status,
    )

    return {
        "recovery_decision": result.decision.value,
        "recovery_reason": result.reason,
    }


def verify_persistent_outcome(state: SafeAgentState):
    service = PersistentUtilityService(state["db_path"])

    status = verify_persistent_ticket(
        service=service,
        operation_id=state["operation_id"],
        expected_customer_id=state.get("customer_id"),
        expected_issue=state.get("issue"),
    )

    return {
        "verification_status": status.value
    }