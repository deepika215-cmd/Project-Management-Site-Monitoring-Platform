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
        role_required(["ADMIN", "MANAGER"])
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

    # Validate workforce category
    category = db.query(
        WorkforceCategory
    ).filter(
        WorkforceCategory.name == worker.category
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Workforce category not found"
        )

    if category.status != "Active":
        raise HTTPException(
            status_code=400,
            detail="Workforce category is inactive"
        )

    new_worker = Worker(
        **worker.model_dump()
    )

    db.add(new_worker)
    db.commit()
    db.refresh(new_worker)

    return new_worker


# ============================================================
# BULK CREATE WORKERS
# ============================================================

@router.post(
    "/bulk"
)
async def bulk_create_workers(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER"])
    )
):

    # --------------------------------------------------------
    # Validate file name
    # --------------------------------------------------------

    filename = file.filename or ""

    if not filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected"
        )

    if not (
        filename.lower().endswith(".csv")
        or filename.lower().endswith(".xlsx")
    ):
        raise HTTPException(
            status_code=400,
            detail="Only CSV and XLSX files are supported"
        )

    # --------------------------------------------------------
    # Read uploaded file
    # --------------------------------------------------------

    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty"
        )

    rows = []

    # --------------------------------------------------------
    # Read CSV
    # --------------------------------------------------------

    if filename.lower().endswith(".csv"):

        try:

            text = contents.decode("utf-8-sig")

            reader = csv.DictReader(
                io.StringIO(text)
            )

            if not reader.fieldnames:
                raise HTTPException(
                    status_code=400,
                    detail="CSV file does not contain headers"
                )

            # Clean headers
            reader.fieldnames = [
                header.strip()
                if header
                else ""
                for header in reader.fieldnames
            ]

            rows = list(reader)

        except HTTPException:
            raise

        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail="CSV file must be UTF-8 encoded"
            )

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to read CSV file: {str(e)}"
            )

    # --------------------------------------------------------
    # Read Excel
    # --------------------------------------------------------

    elif filename.lower().endswith(".xlsx"):

        try:

            workbook = load_workbook(
                filename=io.BytesIO(contents),
                read_only=True,
                data_only=True
            )

            worksheet = workbook.active

            values = list(
                worksheet.values
            )

            if not values:
                workbook.close()

                raise HTTPException(
                    status_code=400,
                    detail="Excel file is empty"
                )

            headers = [
                str(header).strip()
                if header is not None
                else ""
                for header in values[0]
            ]

            if not any(headers):
                workbook.close()

                raise HTTPException(
                    status_code=400,
                    detail="Excel file does not contain headers"
                )

            for row in values[1:]:

                row_data = {}

                for index, header in enumerate(headers):

                    if header:

                        value = (
                            row[index]
                            if index < len(row)
                            else None
                        )

                        row_data[header] = value

                # Ignore completely empty rows
                if any(
                    value is not None
                    and str(value).strip() != ""
                    for value in row_data.values()
                ):
                    rows.append(row_data)

            workbook.close()

        except HTTPException:
            raise

        except Exception as e:

            raise HTTPException(
                status_code=400,
                detail=f"Unable to read Excel file: {str(e)}"
            )

    # --------------------------------------------------------
    # Check rows
    # --------------------------------------------------------

    if not rows:

        raise HTTPException(
            status_code=400,
            detail="No worker records found in the uploaded file"
        )

    # --------------------------------------------------------
    # Required fields
    # --------------------------------------------------------

    required_fields = [
        "name",
        "role"
    ]

    valid_workers = []
    failed_rows = []

    # --------------------------------------------------------
    # Validate every row FIRST
    # --------------------------------------------------------

    for row_number, original_row in enumerate(
        rows,
        start=2
    ):

        try:

            # Normalize column names
            row = {
                str(key).strip(): value
                for key, value in original_row.items()
                if key is not None
            }

            # ------------------------------------------------
            # Validate required fields
            # ------------------------------------------------

            for field in required_fields:

                value = row.get(field)

                if (
                    value is None
                    or str(value).strip() == ""
                ):

                    raise ValueError(
                        f"{field} is required"
                    )

            # ------------------------------------------------
            # Name
            # ------------------------------------------------

            name = str(
                row["name"]
            ).strip()

            # ------------------------------------------------
            # Role
            # ------------------------------------------------

            role = str(
                row["role"]
            ).strip()

            # ------------------------------------------------
            # Phone
            # ------------------------------------------------

            phone = row.get("phone")

            if phone is not None:

                phone = str(
                    phone
                ).strip()

                if phone == "":
                    phone = None

            # ------------------------------------------------
            # Email
            # ------------------------------------------------

            email = row.get("email")

            if email is not None:

                email = str(
                    email
                ).strip()

                if email == "":
                    email = None

            # ------------------------------------------------
            # Category
            # ------------------------------------------------

            category_name = row.get(
                "category"
            )

            if (
                category_name is None
                or str(category_name).strip() == ""
            ):

                category_name = "Skilled Worker"

            else:

                category_name = str(
                    category_name
                ).strip()

            # ------------------------------------------------
            # Skill Type
            # ------------------------------------------------

            skill_type = row.get(
                "skill_type"
            )

            if skill_type is not None:

                skill_type = str(
                    skill_type
                ).strip()

                if skill_type == "":
                    skill_type = None

            # ------------------------------------------------
            # Contractor ID
            # ------------------------------------------------

            contractor_id = row.get(
                "contractor_id"
            )

            if (
                contractor_id is not None
                and str(contractor_id).strip() != ""
            ):

                try:

                    contractor_id = int(
                        float(contractor_id)
                    )

                except (
                    ValueError,
                    TypeError
                ):

                    raise ValueError(
                        "contractor_id must be a valid integer"
                    )

                contractor = db.query(
                    Contractor
                ).filter(
                    Contractor.id == contractor_id
                ).first()

                if not contractor:

                    raise ValueError(
                        f"Contractor {contractor_id} not found"
                    )

            else:

                contractor_id = None

            # ------------------------------------------------
            # Joining Date
            # ------------------------------------------------

            joining_date = row.get(
                "joining_date"
            )

            if joining_date is not None:

                # Excel may return a datetime/date object
                if isinstance(
                    joining_date,
                    (datetime, date)
                ):

                    joining_date = joining_date.strftime(
                        "%Y-%m-%d"
                    )

                else:

                    joining_date = str(
                        joining_date
                    ).strip()

                if joining_date == "":
                    joining_date = None

            # ------------------------------------------------
            # Status
            # ------------------------------------------------

            status = row.get(
                "status"
            )

            if (
                status is None
                or str(status).strip() == ""
            ):

                status = "Active"

            else:

                status = str(
                    status
                ).strip()

            # ------------------------------------------------
            # Validate workforce category
            # ------------------------------------------------

            category = db.query(
                WorkforceCategory
            ).filter(
                WorkforceCategory.name
                == category_name
            ).first()

            if not category:

                raise ValueError(
                    f"Workforce category "
                    f"'{category_name}' not found"
                )

            if category.status != "Active":

                raise ValueError(
                    f"Workforce category "
                    f"'{category_name}' is inactive"
                )

            # ------------------------------------------------
            # Store validated worker data
            # ------------------------------------------------

            valid_workers.append({
                "row": row_number,
                "name": name,
                "role": role,
                "phone": phone,
                "email": email,
                "category": category_name,
                "skill_type": skill_type,
                "contractor_id": contractor_id,
                "joining_date": joining_date,
                "status": status
            })

        except Exception as e:

            failed_rows.append({
                "row": row_number,
                "name": row.get("name"),
                "error": str(e)
            })

    # --------------------------------------------------------
    # Insert all valid workers
    # --------------------------------------------------------

    created_workers = []

    try:

        for worker_data in valid_workers:

            worker = Worker(
                name=worker_data["name"],
                role=worker_data["role"],
                phone=worker_data["phone"],
                email=worker_data["email"],
                category=worker_data["category"],
                skill_type=worker_data["skill_type"],
                contractor_id=worker_data["contractor_id"],
                joining_date=worker_data["joining_date"],
                status=worker_data["status"]
            )

            db.add(worker)

            db.flush()

            created_workers.append({
                "row": worker_data["row"],
                "worker_id": worker.id,
                "name": worker.name
            })

        # Commit all valid workers together
        db.commit()

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Unable to save workers: {str(e)}"
        )

    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return {
        "message": "Bulk worker registration completed",
        "total_rows": len(rows),
        "successful": len(created_workers),
        "failed": len(failed_rows),
        "created_workers": created_workers,
        "failed_rows": failed_rows
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
        role_required(["ADMIN", "MANAGER", "ENGINEER"])
    )
):

    return db.query(
        Worker
    ).order_by(
        Worker.id.desc()
    ).all()


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
        role_required(["ADMIN", "MANAGER", "ENGINEER"])
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
        role_required(["ADMIN", "MANAGER"])
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

    # Validate workforce category
    category = db.query(
        WorkforceCategory
    ).filter(
        WorkforceCategory.name == worker_data.category
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Workforce category not found"
        )

    if category.status != "Active":
        raise HTTPException(
            status_code=400,
            detail="Workforce category is inactive"
        )

    for key, value in worker_data.model_dump().items():
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