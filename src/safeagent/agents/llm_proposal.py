from dataclasses import dataclass


@dataclass(frozen=True)
class OperationProposal:
    operation_type: str


def simulate_llm_proposal(request: str) -> OperationProposal:
    """
    Simulate an LLM selecting an operation.

    No real LLM is called.
    This is only a deterministic test fixture.
    """

    request = request.lower()

    if "disconnect power" in request:
        return OperationProposal(
            operation_type="DISCONNECT_POWER"
        )

    if "create ticket" in request:
        return OperationProposal(
            operation_type="CREATE_TICKET"
        )

    if "read customer" in request:
        return OperationProposal(
            operation_type="READ_CUSTOMER"
        )

    raise ValueError("Unsupported operation request")