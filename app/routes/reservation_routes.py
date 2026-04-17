from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import SessionLocal
from app.models.reservation import Reservation
from app.schemas.reservation import ReservationCreate, ReservationResponse
from app.services.reservation_service import has_room_conflict, has_equipment_conflict
from app.utils.security import get_current_user, require_admin

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/reservations", response_model=ReservationResponse)
def create_reservation(reservation: ReservationCreate, current_user = Depends(get_current_user), db: Session = Depends(get_db)):

    if reservation.room_id is None and reservation.equipment_id is None:
        raise HTTPException(status_code=400, detail="Vous devez spécifier au moins une salle ou un équipement pour la réservation.")

    if reservation.room_id and has_room_conflict(db, reservation.room_id, reservation.start_time, reservation.end_time):
        raise HTTPException(status_code=400, detail="Conflit de réservation: la salle est déjà réservée pour cette période.")
    
    if reservation.equipment_id is not None:
        if has_equipment_conflict(db, reservation.equipment_id, reservation.start_time, reservation.end_time):
            raise HTTPException(status_code=400, detail="Conflit d'équipement: le matériel n'est pas disponible pour cette période.")

    db_reservation = Reservation(user_id=current_user.id,room_id=reservation.room_id, equipment_id=reservation.equipment_id, start_time=reservation.start_time, end_time=reservation.end_time)

    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)

    return db_reservation

@router.get("/reservations")
def get_reservations(db : Session = Depends(get_db), user = Depends(get_current_user)):
    return db.query(Reservation).all()
