"""
Utilitaires de sécurité : hachage de mots de passe, création et validation
des tokens JWT, dépendances FastAPI pour l'authentification et l'autorisation.
"""

import os
import bcrypt
from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User

# ── Configuration JWT ────────────────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable not set")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", 2))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# ── Mots de passe ────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Hache un mot de passe en clair avec bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Vérifie qu'un mot de passe en clair correspond à son hash bcrypt."""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


# ── Tokens JWT ───────────────────────────────────────────────────────────────

def create_access_token(user: User) -> str:
    """
    Crée un token JWT signé contenant l'email et le rôle de l'utilisateur.

    Le token expire après ACCESS_TOKEN_EXPIRE_HOURS heures (défini en .env).
    Le claim 'iat' (issued-at) permet d'auditer l'émission du token.
    """
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {
        "sub": user.email,
        "role": user.role,
        "exp": int(expire.timestamp()),
        "iat": int(datetime.now(timezone.utc).timestamp()),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ── Dépendances FastAPI ──────────────────────────────────────────────────────

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Dépendance FastAPI : décode le token JWT et retourne l'utilisateur correspondant.

    Lève une HTTPException 401 si le token est invalide, expiré ou si
    l'utilisateur n'existe plus en base.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token invalide : champ 'sub' manquant")

        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=401, detail="Utilisateur introuvable")

        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")


def require_admin(current_user: User) -> None:
    """
    Vérifie que l'utilisateur courant possède le rôle 'admin'.

    Lève une HTTPException 403 sinon.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")
