from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    password: str
    role: str = "user"  # "user" ou "admin"

class UserResponse(BaseModel):
    id: int
    email: str
    role: str = "user"  # "user" ou "admin"
    
    class Config:
        from_attributes = True