"""
Modèle SQLAlchemy pour les salles.

Table : room
Colonnes :
    id        PK auto-incrémenté
    name      Nom de la salle (obligatoire)
    capacity  Capacité d'accueil en nombre de personnes
    location  Emplacement physique (bâtiment, étage, numéro de bureau...)
"""

from sqlalchemy import Column, Integer, String
from app.database import Base


class Room(Base):
    __tablename__ = "room"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    capacity = Column(Integer)
    location = Column(String)
