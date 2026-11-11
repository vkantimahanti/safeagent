from dataclasses import dataclass


@dataclass
class PriorAuthorization:
    authorization_id: str
    member_id: str
    procedure_code: str
    status: str


class PriorAuthService:

    def __init__(self):
        self.authorizations = []
        self.operations = {}

    def submit_prior_auth(
        self,
        member_id: str,
        procedure_code: str,
        operation_id: str | None = None,
    ) -> PriorAuthorization:

        if operation_id is not None:
            if operation_id in self.operations:
                existing = self.operations[operation_id]

                if (
                    existing.member_id != member_id
                    or existing.procedure_code != procedure_code
                ):
                    raise ValueError(
                        "Operation ID reused with different request data"
                    )

                return existing

        authorization = PriorAuthorization(
            authorization_id=f"PA-{len(self.authorizations) + 1:04d}",
            member_id=member_id,
            procedure_code=procedure_code,
            status="SUBMITTED",
        )

        self.authorizations.append(authorization)

        if operation_id is not None:
            self.operations[operation_id] = authorization

        return authorization

    def list_authorizations(self):
        return list(self.authorizations)


    def get_authorization_by_operation(
        self,
        operation_id: str,
    ) -> PriorAuthorization | None:
        return self.operations.get(operation_id)