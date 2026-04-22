import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from app.database import SessionLocal
from app.models.user import User
from app.utils.security import hash_password

db = SessionLocal()

admin = User(
    email="admin@test.com",
    password=hash_password("admin123"),
    role="admin"
)

db.add(admin)
db.commit()

print("Admin created")