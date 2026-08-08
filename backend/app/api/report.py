from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.report import Report
from app.schemas.report_schema import (
    ReportCreate,
    ReportResponse,
)

router = APIRouter(
    prefix="/report",
    tags=["Report"],
)


@router.post("/", response_model=ReportResponse)
def create_report(
    report: ReportCreate,
    db: Session = Depends(get_db),
):
    db_report = Report(**report.model_dump())

    db.add(db_report)
    db.commit()
    db.refresh(db_report)

    return db_report


@router.get("/", response_model=list[ReportResponse])
def get_reports(db: Session = Depends(get_db)):
    return db.query(Report).all()


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
):
    report = db.query(Report).filter(
        Report.id == report_id
    ).first()

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not found",
        )

    return report


@router.put("/{report_id}", response_model=ReportResponse)
def update_report(
    report_id: int,
    updated: ReportCreate,
    db: Session = Depends(get_db),
):
    report = db.query(Report).filter(
        Report.id == report_id
    ).first()

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not found",
        )

    for key, value in updated.model_dump().items():
        setattr(report, key, value)

    db.commit()
    db.refresh(report)

    return report


@router.delete("/{report_id}")
def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
):
    report = db.query(Report).filter(
        Report.id == report_id
    ).first()

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not found",
        )

    db.delete(report)
    db.commit()

    return {"message": "Report deleted successfully"}