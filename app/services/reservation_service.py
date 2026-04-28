"""
Service métier pour les réservations.

Contient :
- has_room_conflict()       : détecte les chevauchements sur une salle
- has_equipment_conflict()  : détecte les dépassements de stock sur un équipement
- serialize_reservation()   : convertit un objet SQLAlchemy en ReservationResponse Pydantic
"""

from datetime import datetime

from sqlalchemy.orm import Session

from app.models.reservation import Reservation
from app.models.equipment import Equipment
from app.schemas.reservation import ReservationResponse


def has_room_conflict(db: Session, room_id: int, start_time: datetime, end_time: datetime) -> bool:
    """
    Vérifie s'il existe une réservation qui chevauche la plage horaire demandée
    pour une salle donnée.

    Args:
        db:         Session SQLAlchemy.
        room_id:    Identifiant de la salle.
        start_time: Début de la plage à tester.
        end_time:   Fin de la plage à tester.

    Returns:
        True s'il y a un conflit (la salle est déjà réservée), False sinon.
    """
    conflict = db.query(Reservation).filter(
        Reservation.room_id == room_id,
        Reservation.start_time < end_time,
        Reservation.end_time > start_time
    ).first()
    return conflict is not None


def has_equipment_conflict(db: Session, equipment_id: int, start_time: datetime, end_time: datetime) -> bool:
    """
    Vérifie si le stock disponible d'un équipement est épuisé sur la plage horaire.

    Un équipement avec quantity=N peut être réservé jusqu'à N fois en parallèle.
    Au-delà, la réservation est refusée.

    Args:
        db:           Session SQLAlchemy.
        equipment_id: Identifiant de l'équipement.
        start_time:   Début de la plage à tester.
        end_time:     Fin de la plage à tester.

    Returns:
        True s'il y a un conflit (stock insuffisant ou équipement introuvable), False sinon.
    """
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        return True  # équipement introuvable → on bloque par sécurité

    overlapping = db.query(Reservation).filter(
        Reservation.equipment_id == equipment_id,
        Reservation.start_time < end_time,
        Reservation.end_time > start_time
    ).count()

    return overlapping >= equipment.quantity


def serialize_reservation(r: Reservation) -> ReservationResponse:
    """
    Convertit un objet Reservation SQLAlchemy en schéma Pydantic ReservationResponse,
    en résolvant les noms de salle et d'équipement depuis les relations chargées.

    Les relations `room` et `equipment` doivent être chargées (lazy='joined' sur le modèle).

    Args:
        r: Instance SQLAlchemy Reservation avec relations chargées.

    Returns:
        ReservationResponse avec room_name et equipment_name renseignés si disponibles.
    """
    return ReservationResponse(
        id=r.id,
        user_id=r.user_id,
        room_id=r.room_id,
        equipment_id=r.equipment_id,
        start_time=r.start_time,
        end_time=r.end_time,
        room_name=r.room.name if r.room else None,
        equipment_name=r.equipment.name if r.equipment else None,
    )
