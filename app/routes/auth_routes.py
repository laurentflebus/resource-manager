"""
Routes d'authentification.

Endpoints :
    POST /auth/register  Inscription d'un nouvel utilisateur
    POST /auth/login     Connexion — retourne un token JWT Bearer
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.utils.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Crée un nouveau compte utilisateur avec le rôle 'user' par défaut.

    Le mot de passe est haché avant stockage (bcrypt).
    Retourne une 400 si l'email est déjà utilisé.
    """
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=user.email,
        password=hash_password(user.password),
        role="user"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authentifie un utilisateur et retourne un token JWT Bearer.

    Utilise OAuth2PasswordRequestForm (champs 'username' et 'password'),
    ce qui rend cet endpoint compatible avec le bouton Authorize de Swagger UI.

    Retourne une 401 si les identifiants sont incorrects.
    """
    db_user = db.query(User).filter(User.email == form.username).first()

    if not db_user or not verify_password(form.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(db_user)
    return {"access_token": token, "token_type": "bearer"}
