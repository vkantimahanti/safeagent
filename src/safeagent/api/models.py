from pydantic import BaseModel, Field


class TicketCreateRequest(BaseModel):
    customer_id: str = Field(min_length=1)
    issue: str = Field(min_length=1)
    operation_id: str = Field(min_length=1)


class TicketResponse(BaseModel):
    ticket_id: str
    customer_id: str
    issue: str
    status: str




class OperationVerificationResponse(BaseModel):
    operation_id: str
    verification_status: str
    ticket_id: str | None = None