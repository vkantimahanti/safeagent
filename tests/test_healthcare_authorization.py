import pytest

from safeagent.healthcare.operations import HealthcareOperation
from safeagent.healthcare.authorization_guard import (
    AuthorizationDenied,
    authorize_healthcare_operation,
)


def test_low_risk_operation_without_approval():
    result = authorize_healthcare_operation(
        HealthcareOperation.CHECK_ELIGIBILITY
    )

    assert result is True


def test_high_risk_operation_without_approval():
    with pytest.raises(AuthorizationDenied):
        authorize_healthcare_operation(
            HealthcareOperation.CANCEL_PRIOR_AUTH
        )


def test_high_risk_operation_with_approval():
    result = authorize_healthcare_operation(
        HealthcareOperation.CANCEL_PRIOR_AUTH,
        approved=True,
    )

    assert result is True


def test_medium_risk_operation_requires_approval():
    with pytest.raises(AuthorizationDenied):
        authorize_healthcare_operation(
            HealthcareOperation.SUBMIT_PRIOR_AUTH
        )