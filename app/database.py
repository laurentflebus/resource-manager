"""
Configuration de la base de données SQLAlchemy.

Fournit :
- engine       : connexion PostgreSQL configurée avec pool
- SessionLocal : factory de sessions SQLAlchemy
- Base         : classe de base pour tous les modèles ORM
- get_db()     : dépendance FastAPI pour injecter une session dans les routes
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("La variable d'environnement DATABASE_URL n'est pas définie.")

_is_sqlite = DATABASE_URL.startswith("sqlite")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if _is_sqlite else {},
    pool_pre_ping=not _is_sqlite,
    **({} if _is_sqlite else {"pool_size": 10, "max_overflow": 20})
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()


def get_db():
    """
    Dépendance FastAPI : ouvre une session DB, la fournit à la route,
    puis la ferme proprement après la réponse (même en cas d'erreur).

    Usage dans une route :
        def my_route(db: Session = Depends(get_db)): ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
