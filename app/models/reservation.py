"""
Modèle SQLAlchemy pour les réservations.

Table : reservation
Colonnes :
    id            PK auto-incrémenté
    user_id       Référence à l'utilisateur ayant créé la réservation
    room_id       FK vers room (null si réservation d'équipement)
    equipment_id  FK vers equipment (null si réservation de salle)
    start_time    Début de la réservation (UTC)
    end_time      Fin de la réservation (UTC)

Relations (lazy='joined') :
    room       Chargé automatiquement en JOIN — donne accès à room.name, room.location
    equipment  Chargé automatiquement en JOIN — donne accès à equipment.name

Note :
    Une réservation porte soit room_id, soit equipment_id, jamais les deux.
    Cette contrainte est enforced au niveau du service et des routes.
"""

from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Reservation(Base):
    __tablename__ = "reservation"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    room_id = Column(Integer, ForeignKey("room.id"), nullable=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

    # Relations chargées en JOIN pour éviter les requêtes N+1
    room = relationship("Room", lazy="joined")
    equipment = relationship("Equipment", lazy="joined")
