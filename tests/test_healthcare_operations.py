from safeagent.healthcare.operations import (
    HealthcareOperation,
    HEALTHCARE_OPERATIONS,
)
from safeagent.recovery.risk_aware import OperationRisk


def test_healthcare_operation_registry():

    assert len(HEALTHCARE_OPERATIONS) == 3

    eligibility = HEALTHCARE_OPERATIONS[
        HealthcareOperation.CHECK_ELIGIBILITY
    ]

    prior_auth = HEALTHCARE_OPERATIONS[
        HealthcareOperation.SUBMIT_PRIOR_AUTH
    ]

    cancellation = HEALTHCARE_OPERATIONS[
        HealthcareOperation.CANCEL_PRIOR_AUTH
    ]

    assert eligibility.risk == OperationRisk.LOW

    assert prior_auth.risk == OperationRisk.MEDIUM
    assert prior_auth.requires_authorization is True

    assert cancellation.risk == OperationRisk.HIGH
    assert cancellation.requires_authorization is True