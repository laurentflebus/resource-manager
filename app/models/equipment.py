"""
Modèle SQLAlchemy pour les équipements.

Table : equipment
Colonnes :
    id        PK auto-incrémenté
    name      Nom de l'équipement (obligatoire)
    quantity  Nombre d'unités disponibles (défaut : 1).
              Détermine combien de réservations simultanées sont autorisées
              — voir has_equipment_conflict() dans reservation_service.
"""

from sqlalchemy import Column, Integer, String
from app.database import Base


class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    quantity = Column(Integer, default=1)
