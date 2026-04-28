"""
Fixtures partagées pour tous les tests.

Architecture de test :
- SQLite en mémoire avec StaticPool (connexion unique partagée entre threads)
- Chaque test reçoit des tables fraîches via setup_database (autouse)
- Le TestClient FastAPI utilise la même connexion via override de get_db
- Variables d'environnement mockées avant tout import de l'app
"""

import os
import pytest

# Variables d'env avant tout import de l'app ─────────────────────────────────
os.environ["SECRET_KEY"] = "test-secret-key-for-pytest-only"
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["ACCESS_TOKEN_EXPIRE_HOURS"] = "2"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

import app.database as db_module
from app.database import Base, get_db
from app.main import app
from app.models.user import User
from app.models.room import Room
from app.models.equipment import Equipment
from app.models.reservation import Reservation
from app.utils.security import hash_password, create_access_token

# StaticPool : une seule connexion SQLite partagée entre tous les threads.
# Indispensable pour que le TestClient (thread séparé) voie les données
# créées par la fixture db (thread principal).
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)

# Override du module database pour que toute l'app utilise ce moteur
db_module.engine = test_engine
db_module.SessionLocal = TestingSessionLocal


@pytest.fixture(autouse=True)
def setup_database():
    """Recrée toutes les tables avant chaque test, les supprime après."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db():
    """Session SQLAlchemy isolée pour les tests unitaires de service."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def client(db):
    """TestClient avec get_db remplacé par la session de test."""
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── Fixtures de données ───────────────────────────────────────────────────────

@pytest.fixture
def user(db):
    u = User(email="user@test.com", password=hash_password("password123"), role="user")
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@pytest.fixture
def admin(db):
    a = User(email="admin@test.com", password=hash_password("admin123"), role="admin")
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


@pytest.fixture
def user_token(user):
    return create_access_token(user)


@pytest.fixture
def admin_token(admin):
    return create_access_token(admin)


@pytest.fixture
def room(db):
    r = Room(name="Salle A", capacity=10, location="Bâtiment 1")
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@pytest.fixture
def equipment(db):
    e = Equipment(name="Projecteur", quantity=2)
    db.add(e)
    db.commit()
    db.refresh(e)
    return e
