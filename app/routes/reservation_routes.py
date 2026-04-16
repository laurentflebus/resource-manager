from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import SessionLocal
from app.models.reservation import Reservation
from app.schemas.reservation import ReservationResponse
from app.services.reservation_service import has_room_conflict, has_equipment_conflict

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/reservation", response_model=ReservationResponse)
def create_reservation(reservation: ReservationResponse, db: Session = Depends(get_db)):

    if reservation.room_id is None and reservation.equipment_id is None:
        raise HTTPException(status_code=400, detail="Vous devez spécifier au moins une salle ou un équipement pour la réservation.")

    if reservation.room_id and has_room_conflict(db, reservation.room_id, reservation.start_time, reservation.end_time):
        raise HTTPException(status_code=400, detail="Conflit de réservation: la salle est déjà réservée pour cette période.")
    
    if reservation.equipment_id and has_equipment_conflict(db, reservation.equipment_id, reservation.start_time, reservation.end_time):
        raise HTTPException(status_code=400, detail="Conflit d'équipement: le matériel n'est pas disponible pour cette période.")

    reservation = Reservation(room_id=reservation.room_id, start_time=reservation.start_time, end_time=reservation.end_time)

    db.add(reservation)
    db.commit()
    db.refresh(reservation)

    return reservation
