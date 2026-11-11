from typing import TypedDict

class SafeAgentState(TypedDict, total=False):
    # Business request
    operation_type: str
    operation_id: str
    customer_id: str
    issue: str

    # Trusted policy information
    risk: str
    requires_authorization: bool

    authorization_granted: bool
    authorized: bool

    # Execution results
    ticket_id: str | None
    simulated_verification_status: str
    verification_status: str | None
    recovery_decision: str | None
    error: str | None

    tool_executed: bool

    recovery_reason: str

    workflow_status: str

    db_path: str
