from safeagent.healthcare.operations import (
    HealthcareOperation,
    HEALTHCARE_OPERATIONS,
)


class AuthorizationDenied(Exception):
    pass


def authorize_healthcare_operation(
    operation: HealthcareOperation,
    approved: bool = False,
) -> bool:
    definition = HEALTHCARE_OPERATIONS[operation]

    if definition.requires_authorization and not approved:
        raise AuthorizationDenied(
            f"Authorization required for {operation.value}"
        )

    return True