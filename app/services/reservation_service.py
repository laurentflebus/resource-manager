# Foction de detection de conflits / anti double réservation
from app.models.reservation import Reservation
from sqlalchemy.orm import Session
from datetime import datetime



def is_conflict(db: Session, room_id: int, start_time:datetime, end_time:datetime) -> bool:
    """
    Check if there is a reservation conflict for a given room and time period.

    This function queries the database to determine if any existing reservation
    for the specified room overlaps with the given start and end times.

    Args:
        db (Session): The database session used to query reservations.
        room_id (int): The ID of the room to check for conflicts.
        start_time (datetime): The start time of the proposed reservation.
        end_time (datetime): The end time of the proposed reservation.

    Returns:
        bool: True if there is a conflict (overlapping reservation exists), False otherwise.
    """
    # Vérifie s'il existe une réservation pour la même salle qui chevauche les heures données
    conflict = db.query(Reservation).filter(
        Reservation.room_id == room_id,
        Reservation.start_time < end_time,
        Reservation.end_time > start_time
    ).first()
    return conflict is not None