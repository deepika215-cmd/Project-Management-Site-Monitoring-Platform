from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.invoice import Invoice
from app.models.vendor import Vendor
from app.models.purchase_order import PurchaseOrder
from app.models.project import Project
from app.models.user import User

from app.schemas.invoice_schema import (
    InvoiceCreate,
    InvoiceResponse,
)

from app.core.permissions import role_required


router = APIRouter(
    prefix="/invoices",
    tags=["Invoices"],
)


# ============================================================
# CREATE INVOICE
# Allowed: ADMIN, PROJECT_MANAGER
# ============================================================

@router.post(
    "/",
    response_model=InvoiceResponse,
)
def create_invoice(
    invoice: InvoiceCreate,
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "PROJECT_MANAGER",
        ])
    ),
    db: Session = Depends(get_db),
):

    vendor = (
        db.query(Vendor)
        .filter(Vendor.id == invoice.vendor_id)
        .first()
    )

    if not vendor:
        raise HTTPException(
            status_code=404,
            detail="Vendor not found",
        )

    purchase_order = (
        db.query(PurchaseOrder)
        .filter(
            PurchaseOrder.id == invoice.purchase_order_id
        )
        .first()
    )

    if not purchase_order:
        raise HTTPException(
            status_code=404,
            detail="Purchase order not found",
        )

    project = (
        db.query(Project)
        .filter(Project.id == invoice.project_id)
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    if invoice.invoice_amount < 0:
        raise HTTPException(
            status_code=400,
            detail="Invoice amount cannot be negative",
        )

    existing = (
        db.query(Invoice)
        .filter(
            Invoice.invoice_number
            == invoice.invoice_number
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Invoice number already exists",
        )

    new_invoice = Invoice(
        **invoice.model_dump()
    )

    db.add(new_invoice)
    db.commit()
    db.refresh(new_invoice)

    return new_invoice


# ============================================================
# GET ALL INVOICES
# Allowed: ADMIN, PROJECT_MANAGER, SITE_ENGINEER
# ============================================================

@router.get(
    "/",
    response_model=list[InvoiceResponse],
)
def get_invoices(
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "PROJECT_MANAGER",
            "SITE_ENGINEER",
        ])
    ),
    db: Session = Depends(get_db),
):
    return db.query(Invoice).all()


# ============================================================
# GET INVOICE BY ID
# Allowed: ADMIN, PROJECT_MANAGER, SITE_ENGINEER
# ============================================================

@router.get(
    "/{invoice_id}",
    response_model=InvoiceResponse,
)
def get_invoice(
    invoice_id: int,
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "PROJECT_MANAGER",
            "SITE_ENGINEER",
        ])
    ),
    db: Session = Depends(get_db),
):

    invoice = (
        db.query(Invoice)
        .filter(
            Invoice.id == invoice_id
        )
        .first()
    )

    if not invoice:
        raise HTTPException(
            status_code=404,
            detail="Invoice not found",
        )

    return invoice


# ============================================================
# UPDATE INVOICE
# Allowed: ADMIN, PROJECT_MANAGER
# ============================================================

@router.put(
    "/{invoice_id}",
    response_model=InvoiceResponse,
)
def update_invoice(
    invoice_id: int,
    invoice_data: InvoiceCreate,
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "PROJECT_MANAGER",
        ])
    ),
    db: Session = Depends(get_db),
):

    invoice = (
        db.query(Invoice)
        .filter(
            Invoice.id == invoice_id
        )
        .first()
    )

    if not invoice:
        raise HTTPException(
            status_code=404,
            detail="Invoice not found",
        )

    duplicate = (
        db.query(Invoice)
        .filter(
            Invoice.invoice_number
            == invoice_data.invoice_number,
            Invoice.id != invoice_id,
        )
        .first()
    )

    if duplicate:
        raise HTTPException(
            status_code=400,
            detail="Invoice number already exists",
        )

    for key, value in invoice_data.model_dump().items():
        setattr(invoice, key, value)

    db.commit()
    db.refresh(invoice)

    return invoice


# ============================================================
# UPDATE INVOICE STATUS
#
# Workflow:
#
# Received -> Verified
# Received -> Rejected
# Verified -> Approved
# Verified -> Rejected
# Approved -> Rejected
#
# Allowed: ADMIN, PROJECT_MANAGER
# ============================================================

@router.put(
    "/{invoice_id}/status/{new_status}",
    response_model=InvoiceResponse,
)
def update_invoice_status(
    invoice_id: int,
    new_status: str,
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "PROJECT_MANAGER",
        ])
    ),
    db: Session = Depends(get_db),
):

    invoice = (
        db.query(Invoice)
        .filter(
            Invoice.id == invoice_id
        )
        .first()
    )

    if not invoice:
        raise HTTPException(
            status_code=404,
            detail="Invoice not found",
        )

    allowed_statuses = [
        "Received",
        "Verified",
        "Approved",
        "Rejected",
    ]

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid invoice status. Allowed statuses: "
                "Received, Verified, Approved, Rejected"
            ),
        )

    current_status = invoice.invoice_status

    valid_transitions = {
        "Received": [
            "Verified",
            "Rejected",
        ],
        "Verified": [
            "Approved",
            "Rejected",
        ],
        "Approved": [
            "Rejected",
        ],
        "Rejected": [],
    }

    if new_status == current_status:
        raise HTTPException(
            status_code=400,
            detail="Invoice already has this status",
        )

    if new_status not in valid_transitions.get(
        current_status,
        [],
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                f"Cannot change invoice status "
                f"from {current_status} to {new_status}"
            ),
        )

    invoice.invoice_status = new_status

    db.commit()
    db.refresh(invoice)

    return invoice

# ============================================================
# UPDATE PAYMENT STATUS
#
# Payment Workflow:
#
# Pending -> Partially Paid
# Pending -> Paid
# Pending -> Overdue
# Partially Paid -> Paid
# Partially Paid -> Overdue
# Overdue -> Partially Paid
# Overdue -> Paid
#
# Allowed: ADMIN, PROJECT_MANAGER
# ============================================================

@router.put(
    "/{invoice_id}/payment-status/{new_status}",
    response_model=InvoiceResponse,
)
def update_payment_status(
    invoice_id: int,
    new_status: str,
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "PROJECT_MANAGER",
        ])
    ),
    db: Session = Depends(get_db),
):

    invoice = (
        db.query(Invoice)
        .filter(
            Invoice.id == invoice_id
        )
        .first()
    )

    if not invoice:
        raise HTTPException(
            status_code=404,
            detail="Invoice not found",
        )

    allowed_statuses = [
        "Pending",
        "Partially Paid",
        "Paid",
        "Overdue",
    ]

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid payment status. Allowed statuses: "
                "Pending, Partially Paid, Paid, Overdue"
            ),
        )

    current_status = invoice.payment_status

    valid_transitions = {
        "Pending": [
            "Partially Paid",
            "Paid",
            "Overdue",
        ],
        "Partially Paid": [
            "Paid",
            "Overdue",
        ],
        "Paid": [],
        "Overdue": [
            "Partially Paid",
            "Paid",
        ],
    }

    if new_status == current_status:
        raise HTTPException(
            status_code=400,
            detail="Invoice already has this payment status",
        )

    if new_status not in valid_transitions.get(
        current_status,
        [],
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                f"Cannot change payment status "
                f"from {current_status} to {new_status}"
            ),
        )

    invoice.payment_status = new_status

    db.commit()
    db.refresh(invoice)

    return invoice
# ============================================================
# MARK INVOICE AS PAID
# Allowed: ADMIN, PROJECT_MANAGER
# ============================================================

@router.put(
    "/{invoice_id}/pay",
    response_model=InvoiceResponse,
)
def pay_invoice(
    invoice_id: int,
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "PROJECT_MANAGER",
        ])
    ),
    db: Session = Depends(get_db),
):

    invoice = (
        db.query(Invoice)
        .filter(
            Invoice.id == invoice_id
        )
        .first()
    )

    if not invoice:
        raise HTTPException(
            status_code=404,
            detail="Invoice not found",
        )

    if invoice.payment_status == "Paid":
        raise HTTPException(
            status_code=400,
            detail="Invoice is already paid",
        )

    if invoice.payment_status not in [
        "Pending",
        "Partially Paid",
        "Overdue",
    ]:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invoice cannot be marked as paid "
                "from its current payment status"
            ),
        )

    invoice.payment_status = "Paid"

    db.commit()
    db.refresh(invoice)

    return invoice


# ============================================================
# MARK INVOICE AS OVERDUE
# Allowed: ADMIN, PROJECT_MANAGER
# ============================================================

@router.put(
    "/{invoice_id}/overdue",
    response_model=InvoiceResponse,
)
def mark_invoice_overdue(
    invoice_id: int,
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "PROJECT_MANAGER",
        ])
    ),
    db: Session = Depends(get_db),
):

    invoice = (
        db.query(Invoice)
        .filter(
            Invoice.id == invoice_id
        )
        .first()
    )

    if not invoice:
        raise HTTPException(
            status_code=404,
            detail="Invoice not found",
        )

    if invoice.payment_status == "Paid":
        raise HTTPException(
            status_code=400,
            detail="Paid invoice cannot be marked overdue",
        )

    invoice.payment_status = "Overdue"

    db.commit()
    db.refresh(invoice)

    return invoice


# ============================================================
# DELETE INVOICE
# Allowed: ADMIN
# ============================================================

@router.delete("/{invoice_id}")
def delete_invoice(
    invoice_id: int,
    current_user: User = Depends(
        role_required(["ADMIN"])
    ),
    db: Session = Depends(get_db),
):

    invoice = (
        db.query(Invoice)
        .filter(
            Invoice.id == invoice_id
        )
        .first()
    )

    if not invoice:
        raise HTTPException(
            status_code=404,
            detail="Invoice not found",
        )

    db.delete(invoice)
    db.commit()

    return {
        "message": "Invoice deleted successfully"
    }