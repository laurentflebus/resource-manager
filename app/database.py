from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager
import os
from dotenv import load_dotenv

load_dotenv()

# Échec rapide si la variable est absente
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("La variable d'environnement DATABASE_URL n'est pas définie.")

# Pool de connexions pour la production
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()

# Gestionnaire de contexte pour les sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()