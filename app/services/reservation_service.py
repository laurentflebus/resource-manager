# Foction de detection de conflits / anti double réservation
from app.models.reservation import Reservation
from app.models.equipment import Equipment
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime



def has_room_conflict(db: Session, room_id: int, start_time:datetime, end_time:datetime) -> bool:
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

def has_equipment_conflict(db: Session, equipment_id: int, start_time:datetime, end_time:datetime) -> bool:
    """
    Check if there is an equipment conflict for a given equipment and time period.

    This function verifies if the requested equipment is available during the specified time
    by checking the number of overlapping reservations against the equipment's available quantity.

    Args:
        db (Session): The database session used to query equipment and reservations.
        equipment_id (int): The ID of the equipment to check for conflicts.
        start_time (datetime): The start time of the proposed reservation.
        end_time (datetime): The end time of the proposed reservation.

    Returns:
        bool: True if there is a conflict (not enough equipment available), False otherwise.
    """
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        return True # equipment not found
    
    overlapping_reservations = db.query(Reservation).filter(
        Reservation.equipment_id == equipment_id,
        Reservation.start_time < end_time,
        Reservation.end_time > start_time
    ).count()
    
    return overlapping_reservations >= equipment.quantity
    