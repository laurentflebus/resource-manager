"""
Schémas Pydantic pour les équipements.

Classes :
    EquipmentBase    Champs communs (name, quantity)
    EquipmentCreate  Payload d'entrée pour POST /equipments
    EquipmentUpdate  Payload pour PUT /equipments/{id} (champs optionnels)
    EquipmentResponse  Schéma de sortie incluant l'id
"""

from pydantic import BaseModel
from typing import Optional


class EquipmentBase(BaseModel):
    name: str
    quantity: int = 1


class EquipmentCreate(EquipmentBase):
    """Payload attendu pour créer un équipement."""
    pass


class EquipmentUpdate(BaseModel):
    """Payload pour mettre à jour un équipement. Tous les champs sont optionnels."""
    name: Optional[str] = None
    quantity: Optional[int] = None


class EquipmentResponse(EquipmentBase):
    """Schéma de réponse incluant l'identifiant de l'équipement."""
    id: int

    model_config = {"from_attributes": True}
