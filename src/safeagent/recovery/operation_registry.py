from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from safeagent.recovery.risk_aware import OperationRisk


class OperationType(str, Enum):
    READ_CUSTOMER = "READ_CUSTOMER"
    CREATE_TICKET = "CREATE_TICKET"
    DISCONNECT_POWER = "DISCONNECT_POWER"


class OperationDefinition(BaseModel):
    model_config = ConfigDict(frozen=True)

    operation_type: OperationType
    risk: OperationRisk
    requires_authorization: bool = False
    description: str = Field(min_length=1)


OPERATION_REGISTRY = {
    OperationType.READ_CUSTOMER: OperationDefinition(
        operation_type=OperationType.READ_CUSTOMER,
        risk=OperationRisk.LOW,
        requires_authorization=False,
        description="Read customer account information.",
    ),
    OperationType.CREATE_TICKET: OperationDefinition(
        operation_type=OperationType.CREATE_TICKET,
        risk=OperationRisk.MEDIUM,
        requires_authorization=False,
        description="Create a utility service ticket.",
    ),
    OperationType.DISCONNECT_POWER: OperationDefinition(
        operation_type=OperationType.DISCONNECT_POWER,
        risk=OperationRisk.HIGH,
        requires_authorization=True,
        description="Disconnect electricity service.",
    ),
}


def get_operation_definition(
    operation_type: OperationType,
) -> OperationDefinition:
    try:
        return OPERATION_REGISTRY[operation_type]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported operation type: {operation_type}"
        ) from exc