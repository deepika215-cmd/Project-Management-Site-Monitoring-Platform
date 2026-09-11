import os
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form
)

from fastapi.responses import FileResponse

from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.core.permissions import role_required
from app.core.auth import get_current_user

from app.models.document import Document
from app.models.project import Project
from app.models.user import User

from app.schemas.document_schema import DocumentResponse


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ============================================================
# DOCUMENT STORAGE DIRECTORY
# ============================================================

BACKEND_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIRECTORY = BACKEND_DIR / "uploads" / "documents"
MAX_UPLOAD_SIZE_BYTES = 15 * 1024 * 1024
ALLOWED_DOCUMENT_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".png", ".jpg", ".jpeg"}
ALLOWED_DOCUMENT_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "image/png",
    "image/jpeg",
}
DOCUMENT_READ_ROLES = ["ADMIN", "PROJECT_MANAGER", "SITE_ENGINEER", "CONTRACTOR", "CLIENT"]
DOCUMENT_WRITE_ROLES = ["ADMIN", "PROJECT_MANAGER", "SITE_ENGINEER", "CONTRACTOR"]

UPLOAD_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True
)


def resolve_document_path(stored_path: str) -> Path:
    """Resolve old/new relative document paths against the backend folder."""
    path = Path(stored_path)
    return path if path.is_absolute() else BACKEND_DIR / path


# ============================================================
# UPLOAD DOCUMENT
# ============================================================

@router.post(
    "/",
    response_model=DocumentResponse,
    dependencies=[Depends(role_required(DOCUMENT_WRITE_ROLES))]
)
def upload_document(
    file: UploadFile = File(...),
    category: str | None = Form(None),
    description: str | None = Form(None),
    # Compatibility aliases used by older Angular builds.
    title: str | None = Form(None),
    document_type: str | None = Form(None),
    project_id: int | None = Form(None),
    uploaded_by: int | None = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    # --------------------------------------------------------
    # Validate file name
    # --------------------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="File name is required"
        )

    effective_category = str(category or document_type or '').strip()
    effective_description = str(description or title or '').strip() or None

    if not effective_category:
        raise HTTPException(
            status_code=400,
            detail="Document type/category is required"
        )

    # --------------------------------------------------------
    # Validate project
    # --------------------------------------------------------

    if project_id is not None:

        project = db.query(Project).filter(
            Project.id == project_id
        ).first()

        if not project:
            raise HTTPException(
                status_code=404,
                detail="Project not found"
            )

    # --------------------------------------------------------
    # Validate user
    # --------------------------------------------------------

    if uploaded_by is not None:

        user = db.query(User).filter(
            User.id == uploaded_by
        ).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

    # --------------------------------------------------------
    # Create safe file name
    # --------------------------------------------------------

    original_name = os.path.basename(
        file.filename
    )

    _, extension = os.path.splitext(original_name.lower())
    if extension not in ALLOWED_DOCUMENT_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Allowed: PDF, Word, Excel, PNG and JPG.",
        )

    if file.content_type and file.content_type not in ALLOWED_DOCUMENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file content type.",
        )

    file_path = UPLOAD_DIRECTORY / original_name

    # --------------------------------------------------------
    # Avoid overwriting existing files
    # --------------------------------------------------------

    base_name, extension = os.path.splitext(
        original_name
    )

    counter = 1

    while os.path.exists(file_path):

        new_name = (
            f"{base_name}_{counter}"
            f"{extension}"
        )

        file_path = UPLOAD_DIRECTORY / new_name

        counter += 1

    stored_file_name = file_path.name

    # --------------------------------------------------------
    # Save file
    # --------------------------------------------------------

    bytes_written = 0
    with open(file_path, "wb") as buffer:
        while True:
            chunk = file.file.read(1024 * 1024)
            if not chunk:
                break
            bytes_written += len(chunk)
            if bytes_written > MAX_UPLOAD_SIZE_BYTES:
                buffer.close()
                if os.path.exists(file_path):
                    os.remove(file_path)
                raise HTTPException(
                    status_code=413,
                    detail="File size exceeds the 15 MB upload limit.",
                )
            buffer.write(chunk)

    # --------------------------------------------------------
    # Get file size
    # --------------------------------------------------------

    file_size = file_path.stat().st_size

    # --------------------------------------------------------
    # Create database record
    # --------------------------------------------------------

    new_document = Document(
        file_name=stored_file_name,
        file_path=(Path("uploads") / "documents" / stored_file_name).as_posix(),
        file_type=file.content_type,
        file_size=file_size,
        category=effective_category,
        description=effective_description,
        project_id=project_id,
        uploaded_by=current_user.id
    )

    db.add(new_document)

    db.commit()

    db.refresh(new_document)

    return new_document


# ============================================================
# GET ALL DOCUMENTS
# ============================================================

@router.get(
    "/",
    response_model=list[DocumentResponse],
    dependencies=[Depends(role_required(DOCUMENT_READ_ROLES))]
)
def get_documents(
    project_id: int | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(Document)
    if project_id is not None:
        query = query.filter(Document.project_id == project_id)
    return query.order_by(Document.id.desc()).all()


# ============================================================
# GET DOCUMENT BY ID
# ============================================================

@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    dependencies=[Depends(role_required(DOCUMENT_READ_ROLES))]
)
def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):

    document = db.query(
        Document
    ).filter(
        Document.id == document_id
    ).first()

    if not document:

        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return document


# ============================================================
# DOWNLOAD DOCUMENT
# ============================================================

@router.get(
    "/{document_id}/download",
    dependencies=[Depends(role_required(DOCUMENT_READ_ROLES))]
)
def download_document(
    document_id: int,
    db: Session = Depends(get_db)
):

    document = db.query(
        Document
    ).filter(
        Document.id == document_id
    ).first()

    if not document:

        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    resolved_path = resolve_document_path(document.file_path)

    if not resolved_path.exists():

        raise HTTPException(
            status_code=404,
            detail="Document file not found"
        )

    return FileResponse(
        path=str(resolved_path),
        filename=document.file_name,
        media_type=document.file_type
        or "application/octet-stream"
    )


# ============================================================
# UPDATE DOCUMENT METADATA
# ============================================================

@router.put(
    "/{document_id}",
    response_model=DocumentResponse,
    dependencies=[Depends(role_required(DOCUMENT_WRITE_ROLES))]
)
def update_document(
    document_id: int,
    category: str | None = Form(None),
    description: str | None = Form(None),
    project_id: int | None = Form(None),
    db: Session = Depends(get_db)
):

    document = db.query(
        Document
    ).filter(
        Document.id == document_id
    ).first()

    if not document:

        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    # --------------------------------------------------------
    # Validate project
    # --------------------------------------------------------

    if project_id is not None:

        project = db.query(Project).filter(
            Project.id == project_id
        ).first()

        if not project:

            raise HTTPException(
                status_code=404,
                detail="Project not found"
            )

        document.project_id = project_id

    # --------------------------------------------------------
    # Update metadata
    # --------------------------------------------------------

    if category is not None:
        document.category = category

    if description is not None:
        document.description = description

    db.commit()

    db.refresh(document)

    return document


# ============================================================
# DELETE DOCUMENT
# ============================================================

@router.delete(
    "/{document_id}",
    dependencies=[Depends(role_required(DOCUMENT_WRITE_ROLES))]
)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):

    document = db.query(
        Document
    ).filter(
        Document.id == document_id
    ).first()

    if not document:

        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    # --------------------------------------------------------
    # Delete physical file
    # --------------------------------------------------------

    resolved_path = resolve_document_path(document.file_path)
    if resolved_path.exists():
        resolved_path.unlink()

    # --------------------------------------------------------
    # Delete database record
    # --------------------------------------------------------

    db.delete(document)

    db.commit()

    return {
        "message": "Document deleted successfully",
        "document_id": document_id
    }