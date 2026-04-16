from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.room import Room
from app.schemas.room import RoomCreate, RoomResponse


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/rooms/", response_model=RoomResponse)
def create_room(name: str, capacity: int, location: str, db: Session = Depends(get_db)):
    room = Room(name=name, capacity=capacity, location=location)
    db.add(room)
    db.commit()
    db.refresh(room)
    return room

@router.get("/rooms", response_model=list[RoomResponse]) 
def get_rooms(db: Session = Depends(get_db)):
    return db.query(Room).all()
