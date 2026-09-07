from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File
)
from sqlalchemy.orm import Session

import csv
import io
from datetime import date, datetime
from typing import Any

from openpyxl import load_workbook

from app.database.database import get_db
from app.core.permissions import role_required

from app.models.worker import Worker
from app.models.contractor import Contractor
from app.models.workforce_category import WorkforceCategory
from app.models.user import User

from app.schemas.worker_schema import (
    WorkerCreate,
    WorkerResponse
)


router = APIRouter(
    prefix="/workers",
    tags=["Workers"]
)


DEFAULT_WORKFORCE_CATEGORIES = [
    "Engineer",
    "Supervisor",
    "Contractor",
    "Skilled Worker",
    "Unskilled Worker",
    "Consultant",
]


HEADER_ALIASES = {
    "name": "name",
    "fullname": "name",
    "full_name": "name",
    "workername": "name",
    "worker_name": "name",
    "employee_name": "name",
    "worker": "name",

    "role": "role",
    "designation": "role",
    "jobrole": "role",
    "job_role": "role",
    "workrole": "role",
    "work_role": "role",
    "position": "role",

    "phone": "phone",
    "mobile": "phone",
    "mobilenumber": "phone",
    "mobile_number": "phone",
    "phonenumber": "phone",
    "phone_number": "phone",
    "contact": "phone",
    "contactnumber": "phone",
    "contact_number": "phone",

    "email": "email",
    "emailid": "email",
    "email_id": "email",
    "mail": "email",
    "mailid": "email",

    "category": "category",
    "workforcecategory": "category",
    "workforce_category": "category",
    "worker_category": "category",

    "skill": "skill_type",
    "skilltype": "skill_type",
    "skill_type": "skill_type",
    "worktype": "skill_type",
    "work_type": "skill_type",

    "contractorid": "contractor_id",
    "contractor_id": "contractor_id",
    "contractor": "contractor_id",

    "joiningdate": "joining_date",
    "joining_date": "joining_date",
    "dateofjoining": "joining_date",
    "date_of_joining": "joining_date",
    "join_date": "joining_date",

    "status": "status",
    "active_status": "status",
}


def _normalize_header(header: Any) -> str:
    """Convert user-friendly CSV/XLSX headers to backend field names."""
    if header is None:
        return ""
    raw = str(header).strip()
    key = re_key = raw.lower().replace(" ", "_").replace("-", "_")
    compact = "".join(ch for ch in raw.lower() if ch.isalnum() or ch == "_")
    return HEADER_ALIASES.get(key) or HEADER_ALIASES.get(compact) or key


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    text = str(value).strip()
    if text == "":
        return None
    # Excel sometimes turns mobile numbers into 9876543210.0
    if text.endswith(".0") and text[:-2].isdigit():
        text = text[:-2]
    return text


def _clean_date(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, (datetime, date)):
        return value.strftime("%Y-%m-%d")
    text = _clean_text(value)
    return text


def _ensure_default_categories(db: Session) -> None:
    """Seed common workforce categories so bulk uploads do not fail on fresh DBs."""
    for category_name in DEFAULT_WORKFORCE_CATEGORIES:
        exists = db.query(WorkforceCategory).filter(
            WorkforceCategory.name == category_name
        ).first()
        if not exists:
            db.add(WorkforceCategory(
                name=category_name,
                description=f"Default {category_name.lower()} category",
                status="Active"
            ))
    db.flush()


def _get_or_create_category(db: Session, category_name: str) -> WorkforceCategory:
    category = db.query(WorkforceCategory).filter(
        WorkforceCategory.name == category_name
    ).first()

    if not category:
        category = WorkforceCategory(
            name=category_name,
            description=f"Auto-created during worker bulk registration",
            status="Active"
        )
        db.add(category)
        db.flush()

    if category.status != "Active":
        raise ValueError(f"Workforce category '{category_name}' is inactive")

    return category


def _parse_contractor_id(db: Session, value: Any) -> int | None:
    contractor_value = _clean_text(value)
    if not contractor_value:
        return None

    try:
        contractor_id = int(float(contractor_value))
    except (ValueError, TypeError):
        contractor = db.query(Contractor).filter(
            (Contractor.name == contractor_value) |
            (Contractor.company_name == contractor_value)
        ).first()
        if not contractor:
            raise ValueError(f"Contractor '{contractor_value}' not found")
        return contractor.id

    contractor = db.query(Contractor).filter(Contractor.id == contractor_id).first()
    if not contractor:
        raise ValueError(f"Contractor {contractor_id} not found")
    return contractor.id


def _read_csv_rows(contents: bytes) -> list[dict[str, Any]]:
    try:
        text = contents.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="CSV file must be UTF-8 encoded")

    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise HTTPException(status_code=400, detail="CSV file does not contain headers")

    rows = []
    for source_row in reader:
        normalized = {}
        for key, value in source_row.items():
            normalized_key = _normalize_header(key)
            if normalized_key:
                normalized[normalized_key] = value
        if any(_clean_text(value) for value in normalized.values()):
            rows.append(normalized)
    return rows


def _read_xlsx_rows(contents: bytes) -> list[dict[str, Any]]:
    try:
        workbook = load_workbook(
            filename=io.BytesIO(contents),
            read_only=True,
            data_only=True
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Unable to read Excel file: {exc}")

    try:
        worksheet = workbook.active
        values = list(worksheet.values)

        if not values:
            raise HTTPException(status_code=400, detail="Excel file is empty")

        headers = [_normalize_header(header) for header in values[0]]
        if not any(headers):
            raise HTTPException(status_code=400, detail="Excel file does not contain headers")

        rows: list[dict[str, Any]] = []
        for raw_row in values[1:]:
            row_data = {}
            for index, header in enumerate(headers):
                if header:
                    row_data[header] = raw_row[index] if index < len(raw_row) else None
            if any(_clean_text(value) for value in row_data.values()):
                rows.append(row_data)
        return rows
    finally:
        workbook.close()


def _build_worker_from_row(db: Session, row: dict[str, Any], row_number: int) -> dict[str, Any]:
    name = _clean_text(row.get("name"))
    if not name:
        raise ValueError("name / full_name / worker_name is required")

    role = _clean_text(row.get("role")) or "Worker"
    phone = _clean_text(row.get("phone"))
    email = _clean_text(row.get("email"))
    if email:
        email = email.lower()

    category_name = _clean_text(row.get("category")) or "Skilled Worker"
    _get_or_create_category(db, category_name)

    status = _clean_text(row.get("status")) or "Active"
    if status.lower() in ["active", "yes", "true", "1"]:
        status = "Active"
    elif status.lower() in ["inactive", "no", "false", "0"]:
        status = "Inactive"

    return {
        "row": row_number,
        "name": name,
        "role": role,
        "phone": phone,
        "email": email,
        "category": category_name,
        "skill_type": _clean_text(row.get("skill_type")),
        "contractor_id": _parse_contractor_id(db, row.get("contractor_id")),
        "joining_date": _clean_date(row.get("joining_date")),
        "status": status
    }


# ============================================================
# CREATE WORKER
# ============================================================

@router.post(
    "/",
    response_model=WorkerResponse
)
def create_worker(
    worker: WorkerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "PROJECT_MANAGER", "CONTRACTOR"])
    )
):

    # Validate contractor if supplied
    if worker.contractor_id is not None:

        contractor = db.query(
            Contractor
        ).filter(
            Contractor.id == worker.contractor_id
        ).first()

        if not contractor:
            raise HTTPException(
                status_code=404,
                detail="Contractor not found"
            )

    _ensure_default_categories(db)

    try:
        _get_or_create_category(db, worker.category or "Skilled Worker")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    data = worker.model_dump()
    data["name"] = (data.get("name") or "").strip()
    data["role"] = (data.get("role") or "Worker").strip()
    data["phone"] = _clean_text(data.get("phone"))
    data["email"] = (_clean_text(data.get("email")) or None)
    if data["email"]:
        data["email"] = data["email"].lower()
    data["category"] = data.get("category") or "Skilled Worker"

    new_worker = Worker(**data)

    db.add(new_worker)
    db.commit()
    db.refresh(new_worker)

    return new_worker


# ============================================================
# BULK CREATE WORKERS
# ============================================================

@router.post("/bulk")
async def bulk_create_workers(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "PROJECT_MANAGER", "CONTRACTOR"])
    )
):
    filename = file.filename or ""

    if not filename:
        raise HTTPException(status_code=400, detail="No file selected")

    if not filename.lower().endswith((".csv", ".xlsx")):
        raise HTTPException(status_code=400, detail="Only CSV and XLSX files are supported")

    contents = await file.read()

    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Worker bulk upload file must be below 5 MB")

    rows = _read_csv_rows(contents) if filename.lower().endswith(".csv") else _read_xlsx_rows(contents)

    if not rows:
        raise HTTPException(status_code=400, detail="No worker records found in the uploaded file")

    _ensure_default_categories(db)

    valid_workers: list[dict[str, Any]] = []
    failed_rows: list[dict[str, Any]] = []

    for row_number, row in enumerate(rows, start=2):
        try:
            valid_workers.append(_build_worker_from_row(db, row, row_number))
        except Exception as exc:
            failed_rows.append({
                "row": row_number,
                "name": _clean_text(row.get("name")) or "—",
                "error": str(exc)
            })

    created_workers = []
    skipped_rows = []

    try:
        for worker_data in valid_workers:
            # Avoid duplicate records when the same template is uploaded more than once.
            existing = None
            if worker_data.get("email"):
                existing = db.query(Worker).filter(Worker.email == worker_data["email"]).first()
            if not existing and worker_data.get("phone"):
                existing = db.query(Worker).filter(Worker.phone == worker_data["phone"]).first()

            if existing:
                skipped_rows.append({
                    "row": worker_data["row"],
                    "name": worker_data["name"],
                    "reason": "Worker already exists with same email or phone",
                    "worker_id": existing.id
                })
                continue

            row_number = worker_data.pop("row")
            worker = Worker(**worker_data)
            db.add(worker)
            db.flush()

            created_workers.append({
                "row": row_number,
                "worker_id": worker.id,
                "id": worker.id,
                "name": worker.name,
                "role": worker.role,
                "phone": worker.phone,
                "email": worker.email,
                "category": worker.category,
                "skill_type": worker.skill_type,
                "contractor_id": worker.contractor_id,
                "joining_date": worker.joining_date,
                "status": worker.status
            })

        db.commit()

    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unable to save workers: {exc}")

    return {
        "message": "Bulk worker registration completed",
        "total_rows": len(rows),
        "successful": len(created_workers),
        "created": len(created_workers),
        "failed": len(failed_rows),
        "skipped": len(skipped_rows),
        "created_workers": created_workers,
        "failed_rows": failed_rows,
        "skipped_rows": skipped_rows
    }


@router.get("/bulk-template")
def get_bulk_worker_template(
    current_user: User = Depends(
        role_required(["ADMIN", "PROJECT_MANAGER", "CONTRACTOR"])
    )
):
    """Document the exact CSV/XLSX headers accepted by /workers/bulk."""
    return {
        "supported_formats": ["csv", "xlsx"],
        "required_columns": ["name"],
        "recommended_columns": [
            "name",
            "role",
            "phone",
            "email",
            "category",
            "skill_type",
            "contractor_id",
            "joining_date",
            "status"
        ],
        "accepted_name_headers": ["name", "full_name", "worker_name", "Full Name"],
        "example_rows": [
            {
                "name": "Ravi Kumar",
                "role": "Mason",
                "phone": "9876543210",
                "email": "ravi.worker@buildtrack.com",
                "category": "Skilled Worker",
                "skill_type": "Brick Work",
                "contractor_id": "",
                "joining_date": "2026-09-01",
                "status": "Active"
            }
        ]
    }


# ============================================================
# GET ALL WORKERS
# ============================================================

@router.get(
    "/",
    response_model=list[WorkerResponse]
)
def get_workers(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "PROJECT_MANAGER", "SITE_ENGINEER", "CONTRACTOR", "WORKER"])
    )
):

    query = db.query(Worker)

    if current_user.role == "WORKER":
        query = query.filter(Worker.email == current_user.email)

    return query.order_by(Worker.id.desc()).all()


# ============================================================
# GET WORKER BY ID
# ============================================================

@router.get(
    "/{worker_id}",
    response_model=WorkerResponse
)
def get_worker(
    worker_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "PROJECT_MANAGER", "SITE_ENGINEER", "CONTRACTOR", "WORKER"])
    )
):

    worker = db.query(
        Worker
    ).filter(
        Worker.id == worker_id
    ).first()

    if not worker:
        raise HTTPException(
            status_code=404,
            detail="Worker not found"
        )

    if current_user.role == "WORKER" and worker.email != current_user.email:
        raise HTTPException(status_code=403, detail="You can view only your worker profile")

    return worker


# ============================================================
# UPDATE WORKER
# ============================================================

@router.put(
    "/{worker_id}",
    response_model=WorkerResponse
)
def update_worker(
    worker_id: int,
    worker_data: WorkerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "PROJECT_MANAGER", "CONTRACTOR"])
    )
):

    worker = db.query(
        Worker
    ).filter(
        Worker.id == worker_id
    ).first()

    if not worker:
        raise HTTPException(
            status_code=404,
            detail="Worker not found"
        )

    # Validate contractor
    if worker_data.contractor_id is not None:

        contractor = db.query(
            Contractor
        ).filter(
            Contractor.id == worker_data.contractor_id
        ).first()

        if not contractor:
            raise HTTPException(
                status_code=404,
                detail="Contractor not found"
            )

    _ensure_default_categories(db)

    try:
        _get_or_create_category(db, worker_data.category or "Skilled Worker")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    data = worker_data.model_dump()
    data["name"] = (data.get("name") or "").strip()
    data["role"] = (data.get("role") or "Worker").strip()
    data["phone"] = _clean_text(data.get("phone"))
    data["email"] = (_clean_text(data.get("email")) or None)
    if data["email"]:
        data["email"] = data["email"].lower()
    data["category"] = data.get("category") or "Skilled Worker"

    for key, value in data.items():
        setattr(worker, key, value)

    db.commit()
    db.refresh(worker)

    return worker


# ============================================================
# DELETE WORKER
# ============================================================

@router.delete(
    "/{worker_id}"
)
def delete_worker(
    worker_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN"])
    )
):

    worker = db.query(
        Worker
    ).filter(
        Worker.id == worker_id
    ).first()

    if not worker:
        raise HTTPException(
            status_code=404,
            detail="Worker not found"
        )

    db.delete(worker)
    db.commit()

    return {
        "message": "Worker deleted successfully"
    }
