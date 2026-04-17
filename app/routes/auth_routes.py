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
    # check for no duplicate email => DB integrity error
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code= 400, detail="Email already registered")
    new_user = User(email= user.email, password=hash_password(user.password), role="user")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
# /login uses UserCreate as its request schema — this schema is meant for registration. 
# Use OAuth2PasswordRequestForm instead, which is the FastAPI standard and 
# makes your tokenUrl="auth/login" actually work with Swagger UI
@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.email == form.username).first()

    if not db_user or not verify_password(form.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(db_user)

    return {"access_token": token, "token_type": "bearer"}