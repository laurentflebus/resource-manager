"""
Modèle SQLAlchemy pour les utilisateurs.

Table : user
Colonnes :
    id        PK auto-incrémenté
    email     Adresse email unique (utilisée comme identifiant de connexion)
    password  Hash bcrypt du mot de passe — jamais stocké en clair
    role      Rôle de l'utilisateur : 'user' (défaut) ou 'admin'

Rôles :
    user   Peut créer et consulter ses propres réservations
    admin  Accès complet : voir/modifier/supprimer toutes les réservations
"""

from sqlalchemy import Column, Integer, String
from app.database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="user", nullable=False)
