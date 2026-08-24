from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.payroll import Payroll
from app.models.worker import Worker
from app.schemas.payroll_schema import PayrollCreate, PayrollResponse


router = APIRouter(
    prefix="/payroll",
    tags=["Payroll"]
)


# ============================================================
# CREATE PAYROLL
# ============================================================

@router.post("/", response_model=PayrollResponse)
def create_payroll(
    payroll: PayrollCreate,
    db: Session = Depends(get_db)
):
    # Check whether worker exists
    worker = db.query(Worker).filter(
        Worker.id == payroll.worker_id
    ).first()

    if not worker:
        raise HTTPException(
            status_code=404,
            detail="Worker not found"
        )

    # Calculate estimated pay
    regular_pay = (
        payroll.working_hours * payroll.pay_rate
    )

    overtime_pay = (
        payroll.overtime_hours *
        payroll.pay_rate * 1.5
    )

    estimated_pay = regular_pay + overtime_pay

    db_payroll = Payroll(
        worker_id=payroll.worker_id,
        project_id=payroll.project_id,
        pay_rate=payroll.pay_rate,
        working_days=payroll.working_days,
        working_hours=payroll.working_hours,
        overtime_hours=payroll.overtime_hours,
        leave_days=payroll.leave_days,
        estimated_pay=estimated_pay,
        payroll_status=payroll.payroll_status
    )

    db.add(db_payroll)
    db.commit()
    db.refresh(db_payroll)

    return db_payroll


# ============================================================
# GET ALL PAYROLL RECORDS
# ============================================================

@router.get("/", response_model=list[PayrollResponse])
def get_all_payroll(
    db: Session = Depends(get_db)
):
    return db.query(Payroll).all()


# ============================================================
# GET PAYROLL BY ID
# ============================================================

@router.get("/{payroll_id}", response_model=PayrollResponse)
def get_payroll(
    payroll_id: int,
    db: Session = Depends(get_db)
):
    payroll = db.query(Payroll).filter(
        Payroll.id == payroll_id
    ).first()

    if not payroll:
        raise HTTPException(
            status_code=404,
            detail="Payroll record not found"
        )

    return payroll


# ============================================================
# GET PAYROLL FOR A WORKER
# ============================================================

@router.get(
    "/worker/{worker_id}",
    response_model=list[PayrollResponse]
)
def get_worker_payroll(
    worker_id: int,
    db: Session = Depends(get_db)
):
    worker = db.query(Worker).filter(
        Worker.id == worker_id
    ).first()

    if not worker:
        raise HTTPException(
            status_code=404,
            detail="Worker not found"
        )

    return db.query(Payroll).filter(
        Payroll.worker_id == worker_id
    ).all()


# ============================================================
# UPDATE PAYROLL
# ============================================================

@router.put(
    "/{payroll_id}",
    response_model=PayrollResponse
)
def update_payroll(
    payroll_id: int,
    payroll: PayrollCreate,
    db: Session = Depends(get_db)
):
    db_payroll = db.query(Payroll).filter(
        Payroll.id == payroll_id
    ).first()

    if not db_payroll:
        raise HTTPException(
            status_code=404,
            detail="Payroll record not found"
        )

    worker = db.query(Worker).filter(
        Worker.id == payroll.worker_id
    ).first()

    if not worker:
        raise HTTPException(
            status_code=404,
            detail="Worker not found"
        )

    # Recalculate estimated pay
    regular_pay = (
        payroll.working_hours * payroll.pay_rate
    )

    overtime_pay = (
        payroll.overtime_hours *
        payroll.pay_rate * 1.5
    )

    estimated_pay = regular_pay + overtime_pay

    db_payroll.worker_id = payroll.worker_id
    db_payroll.project_id = payroll.project_id
    db_payroll.pay_rate = payroll.pay_rate
    db_payroll.working_days = payroll.working_days
    db_payroll.working_hours = payroll.working_hours
    db_payroll.overtime_hours = payroll.overtime_hours
    db_payroll.leave_days = payroll.leave_days
    db_payroll.estimated_pay = estimated_pay
    db_payroll.payroll_status = payroll.payroll_status

    db.commit()
    db.refresh(db_payroll)

    return db_payroll


# ============================================================
# DELETE PAYROLL
# ============================================================

@router.delete("/{payroll_id}")
def delete_payroll(
    payroll_id: int,
    db: Session = Depends(get_db)
):
    db_payroll = db.query(Payroll).filter(
        Payroll.id == payroll_id
    ).first()

    if not db_payroll:
        raise HTTPException(
            status_code=404,
            detail="Payroll record not found"
        )

    db.delete(db_payroll)
    db.commit()

    return {
        "message": "Payroll record deleted successfully"
    }


# ============================================================
# UPDATE PAYROLL STATUS
# ============================================================

@router.patch("/{payroll_id}/status")
def update_payroll_status(
    payroll_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    db_payroll = db.query(Payroll).filter(
        Payroll.id == payroll_id
    ).first()

    if not db_payroll:
        raise HTTPException(
            status_code=404,
            detail="Payroll record not found"
        )

    db_payroll.payroll_status = status

    db.commit()
    db.refresh(db_payroll)

    return {
        "message": "Payroll status updated successfully",
        "payroll_id": payroll_id,
        "status": status
    }