from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.material import Material
from app.schemas.material_schema import MaterialCreate, MaterialResponse


router = APIRouter(
    prefix="/materials",
    tags=["Materials"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=MaterialResponse)
def create_material(
    material: MaterialCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(Material).filter(
        Material.name == material.name
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Material already exists"
        )

    new_material = Material(
        name=material.name,
        category=material.category,
        unit=material.unit,
        minimum_stock=material.minimum_stock
    )

    db.add(new_material)
    db.commit()
    db.refresh(new_material)

    return new_material


@router.get("/", response_model=list[MaterialResponse])
def get_materials(
    db: Session = Depends(get_db)
):
    return db.query(Material).all()


@router.get("/{material_id}", response_model=MaterialResponse)
def get_material(
    material_id: int,
    db: Session = Depends(get_db)
):
    material = db.query(Material).filter(
        Material.id == material_id
    ).first()

    if not material:
        raise HTTPException(
            status_code=404,
            detail="Material not found"
        )

    return material
