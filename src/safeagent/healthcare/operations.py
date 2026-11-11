from enum import Enum

from pydantic import BaseModel

from safeagent.recovery.risk_aware import OperationRisk


class HealthcareOperation(str, Enum):
    CHECK_ELIGIBILITY = "CHECK_ELIGIBILITY"
    SUBMIT_PRIOR_AUTH = "SUBMIT_PRIOR_AUTH"
    CANCEL_PRIOR_AUTH = "CANCEL_PRIOR_AUTH"


class HealthcareOperationDefinition(BaseModel):
    operation: HealthcareOperation
    risk: OperationRisk
    requires_authorization: bool
    description: str


HEALTHCARE_OPERATIONS = {
    HealthcareOperation.CHECK_ELIGIBILITY:
        HealthcareOperationDefinition(
            operation=HealthcareOperation.CHECK_ELIGIBILITY,
            risk=OperationRisk.LOW,
            requires_authorization=False,
            description="Retrieve synthetic member eligibility",
        ),

    HealthcareOperation.SUBMIT_PRIOR_AUTH:
        HealthcareOperationDefinition(
            operation=HealthcareOperation.SUBMIT_PRIOR_AUTH,
            risk=OperationRisk.MEDIUM,
            requires_authorization=True,
            description="Submit synthetic prior authorization request",
        ),

    HealthcareOperation.CANCEL_PRIOR_AUTH:
        HealthcareOperationDefinition(
            operation=HealthcareOperation.CANCEL_PRIOR_AUTH,
            risk=OperationRisk.HIGH,
            requires_authorization=True,
            description="Cancel synthetic prior authorization",
        ),
}