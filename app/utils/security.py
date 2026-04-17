import bcrypt
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
import os

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environement variable not set")
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPRIRE_HOURS = int(os.getenv("ACCESS_TOKEN_EXPRIRE_HOURS", 2))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Hash 
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
# Verify
def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))

# Creation du token avec role
def create_access_token(user: User) -> str:
    # Use timezone-aware datetime
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPRIRE_HOURS)
    payload = {
        "sub" : user.email,
        "role" : user.role,
        "exp" : expire,
        "iat": datetime.now(timezone.utc), # (issued-at) claim — useful for token invalidation and auditing
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# Recupérer l'utilisateur à partir du token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid payload token")

        user = db.query(User).filter(User.email == email).first()

        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
# Vérification du role admin
def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return current_user
