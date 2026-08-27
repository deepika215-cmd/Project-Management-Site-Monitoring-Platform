from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict


PaymentStatus = Literal[
    "Pending",
    "Partially Paid",
    "Paid",
    "Overdue",
]

InvoiceStatus = Literal[
    "Received",
    "Verified",
    "Approved",
    "Rejected",
]


class InvoiceCreate(BaseModel):
    invoice_number: str

    vendor_id: int

    purchase_order_id: int

    project_id: int

    invoice_date: date

    due_date: date | None = None

    invoice_amount: float

    payment_status: PaymentStatus = "Pending"

    invoice_status: InvoiceStatus = "Received"

    remarks: str | None = None


class InvoiceResponse(InvoiceCreate):
    id: int

    model_config = ConfigDict(
        from_attributes=True
    )