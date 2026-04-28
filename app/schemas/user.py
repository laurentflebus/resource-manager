"""
Schémas Pydantic pour les utilisateurs.

Classes :
    UserCreate    Payload d'inscription (email + password)
    UserResponse  Réponse publique (sans mot de passe)
"""

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """Payload attendu pour POST /auth/register."""
    email: str
    password: str


class UserResponse(BaseModel):
    """
    Schéma de réponse utilisateur — ne contient jamais le mot de passe.
    Retourné après inscription et utilisable pour afficher le profil.
    """
    id: int
    email: str
    role: str

    model_config = {"from_attributes": True}
