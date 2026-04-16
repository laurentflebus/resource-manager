from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import SessionLocal
from app.models.reservation import Reservation
from app.schemas.reservation import ReservationResponse
from app.services.reservation_service import is_conflict

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/reservations", response_model=ReservationResponse)
def create_reservation(room_id: int, start_time: datetime, end_time: datetime, db: Session = Depends(get_db)):

    if room_id is None and equipment_id is None:
        raise HTTPException(status_code=400, detail="Vous devez spécifier au moins une salle ou un équipement pour la réservation.")

    if room_id and is_conflict(db, room_id, start_time, end_time):
        raise HTTPException(status_code=400, detail="Conflit de réservation: la salle est déjà réservée pour cette période.")
    
    reservation = Reservation(room_id=room_id, start_time=start_time, end_time=end_time)
    
    db.add(reservation)
    db.commit()
    db.refresh(reservation)

    return reservation
