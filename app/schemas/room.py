"""
Schémas Pydantic pour les salles.

Classes :
    RoomBase      Champs communs (name, capacity, location)
    RoomCreate    Payload d'entrée pour POST /rooms
    RoomUpdate    Payload pour PUT /rooms/{id} (champs optionnels)
    RoomResponse  Schéma de sortie incluant l'id
"""

from pydantic import BaseModel
from typing import Optional


class RoomBase(BaseModel):
    name: str
    capacity: int
    location: str


class RoomCreate(RoomBase):
    """Payload attendu pour créer une salle."""
    pass


class RoomUpdate(BaseModel):
    """Payload pour mettre à jour une salle. Tous les champs sont optionnels."""
    name: Optional[str] = None
    capacity: Optional[int] = None
    location: Optional[str] = None


class RoomResponse(RoomBase):
    """Schéma de réponse incluant l'identifiant de la salle."""
    id: int

    model_config = {"from_attributes": True}
