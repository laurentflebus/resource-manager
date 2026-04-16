from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.equipment import Equipment


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/equipments")
def create_equipment(name: str, quantity: int, db: Session = Depends(get_db)):
    equipment = Equipment(name=name, quantity=quantity)
    db.add(equipment)
    db.commit()
    db.refresh(equipment)
    return equipment

@router.get("/equipments")
def get_equipment(db: Session = Depends(get_db)):
    return db.query(Equipment).all()
