"""
Schémas Pydantic pour les réservations.

Classes :
    ReservationBase     Champs communs (room_id, equipment_id, start_time, end_time)
    ReservationCreate   Schéma d'entrée pour POST /reservations (hérite de Base)
    ReservationUpdate   Schéma d'entrée pour PUT /reservations/{id} (tous les champs optionnels)
    ReservationResponse Schéma de sortie enrichi avec user_id, room_name, equipment_name
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ReservationBase(BaseModel):
    room_id: Optional[int] = None
    equipment_id: Optional[int] = None
    start_time: datetime
    end_time: datetime


class ReservationCreate(ReservationBase):
    """Payload attendu pour créer une réservation. room_id ou equipment_id doit être renseigné."""
    pass


class ReservationUpdate(BaseModel):
    """
    Payload pour mettre à jour une réservation (PATCH-like).
    Tous les champs sont optionnels — seuls les champs fournis sont mis à jour.
    """
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    room_id: Optional[int] = None
    equipment_id: Optional[int] = None


class ReservationResponse(BaseModel):
    """
    Schéma de réponse complet retourné par l'API.

    room_name et equipment_name sont résolus depuis les relations SQLAlchemy
    par serialize_reservation() dans reservation_service.py.
    """
    id: int
    user_id: Optional[int] = None
    room_id: Optional[int] = None
    equipment_id: Optional[int] = None
    start_time: datetime
    end_time: datetime
    room_name: Optional[str] = None
    equipment_name: Optional[str] = None

    model_config = {"from_attributes": True}
