import pytest
from pydantic import ValidationError

from safeagent.recovery.operation_registry import (
    OperationDefinition,
    OperationType,
    get_operation_definition,
)

from safeagent.recovery.risk_aware import OperationRisk


def test_read_customer_is_low_risk():
    operation = get_operation_definition(
        OperationType.READ_CUSTOMER
    )

    assert operation.risk == OperationRisk.LOW
    assert operation.requires_authorization is False


def test_create_ticket_is_medium_risk():
    operation = get_operation_definition(
        OperationType.CREATE_TICKET
    )

    assert operation.risk == OperationRisk.MEDIUM
    assert operation.requires_authorization is False


def test_disconnect_power_is_high_risk():
    operation = get_operation_definition(
        OperationType.DISCONNECT_POWER
    )

    assert operation.risk == OperationRisk.HIGH
    assert operation.requires_authorization is True


def test_invalid_risk_is_rejected():
    with pytest.raises(ValidationError):
        OperationDefinition(
            operation_type=OperationType.CREATE_TICKET,
            risk="CRITICAL",
            description="Invalid risk classification.",
        )


def test_unsupported_operation_is_rejected():
    with pytest.raises(ValueError):
        get_operation_definition("UNKNOWN_OPERATION")