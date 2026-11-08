from fastapi import Depends, FastAPI, HTTPException, status

from safeagent.api.dependencies import get_service
from safeagent.api.models import TicketCreateRequest, TicketResponse
from safeagent.api.models import (
    TicketCreateRequest,
    TicketResponse,
    OperationVerificationResponse,
)
from safeagent.services.persistent_utility_service import (
    PersistentUtilityService,
)

app = FastAPI(
    title="SafeAgent API",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "safeagent",
    }


@app.get("/")
def home():
    return {
        "message": "Welcome to SafeAgent API",
        "status": "running",
        "documentation": "/docs",
    }



@app.post(
    "/tickets",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket(
    request: TicketCreateRequest,
    service: PersistentUtilityService = Depends(get_service),
):
    try:
        ticket = service.create_ticket(
            customer_id=request.customer_id,
            issue=request.issue,
            operation_id=request.operation_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Operation ID conflicts with an existing request",
        ) from exc

    return TicketResponse(
        ticket_id=ticket.ticket_id,
        customer_id=ticket.customer_id,
        issue=ticket.issue,
        status=ticket.status,
    )



@app.get(
    "/operations/{operation_id}",
    response_model=OperationVerificationResponse,
)
def verify_operation(
    operation_id: str,
    service: PersistentUtilityService = Depends(get_service),
):
    ticket = service.get_ticket_by_operation(operation_id)

    if ticket is None:
        return OperationVerificationResponse(
            operation_id=operation_id,
            verification_status="UNKNOWN",
            ticket_id=None,
        )

    return OperationVerificationResponse(
        operation_id=operation_id,
        verification_status="SUCCESS",
        ticket_id=ticket.ticket_id,
    )