import os
import shutil

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

UPLOAD_DIRECTORY = "uploads/documents"

os.makedirs(
    UPLOAD_DIRECTORY,
    exist_ok=True
)


# ============================================================
# UPLOAD DOCUMENT
# ============================================================

@router.post(
    "/",
    response_model=DocumentResponse
)
def upload_document(
    file: UploadFile = File(...),
    category: str = Form(...),
    description: str | None = Form(None),
    project_id: int | None = Form(None),
    uploaded_by: int | None = Form(None),
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Validate file name
    # --------------------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="File name is required"
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

    file_path = os.path.join(
        UPLOAD_DIRECTORY,
        original_name
    )

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

        file_path = os.path.join(
            UPLOAD_DIRECTORY,
            new_name
        )

        counter += 1

    stored_file_name = os.path.basename(
        file_path
    )

    # --------------------------------------------------------
    # Save file
    # --------------------------------------------------------

    with open(file_path, "wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    # --------------------------------------------------------
    # Get file size
    # --------------------------------------------------------

    file_size = os.path.getsize(
        file_path
    )

    # --------------------------------------------------------
    # Create database record
    # --------------------------------------------------------

    new_document = Document(
        file_name=stored_file_name,
        file_path=file_path,
        file_type=file.content_type,
        file_size=file_size,
        category=category,
        description=description,
        project_id=project_id,
        uploaded_by=uploaded_by
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
    response_model=list[DocumentResponse]
)
def get_documents(
    db: Session = Depends(get_db)
):

    return db.query(
        Document
    ).order_by(
        Document.id.desc()
    ).all()


# ============================================================
# GET DOCUMENT BY ID
# ============================================================

@router.get(
    "/{document_id}",
    response_model=DocumentResponse
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
    "/{document_id}/download"
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

    if not os.path.exists(
        document.file_path
    ):

        raise HTTPException(
            status_code=404,
            detail="Document file not found"
        )

    return FileResponse(
        path=document.file_path,
        filename=document.file_name,
        media_type=document.file_type
        or "application/octet-stream"
    )


# ============================================================
# UPDATE DOCUMENT METADATA
# ============================================================

@router.put(
    "/{document_id}",
    response_model=DocumentResponse
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
    "/{document_id}"
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

    if os.path.exists(
        document.file_path
    ):

        os.remove(
            document.file_path
        )

    # --------------------------------------------------------
    # Delete database record
    # --------------------------------------------------------

    db.delete(document)

    db.commit()

    return {
        "message": "Document deleted successfully",
        "document_id": document_id
    }