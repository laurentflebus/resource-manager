"""
Configuration de l'environnement Alembic.

Ce fichier est exécuté par Alembic à chaque commande (migrate, upgrade, etc.).
Il connecte Alembic à la base de données et à nos modèles SQLAlchemy.

Points clés :
- DATABASE_URL est lue depuis le fichier .env (via python-dotenv)
- target_metadata pointe vers Base.metadata pour la génération automatique
- Tous les modèles sont importés explicitement pour qu'Alembic les détecte
"""

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# Ajoute la racine du projet au PYTHONPATH pour les imports app.*
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

load_dotenv()

# ── Config Alembic ────────────────────────────────────────────────────────────
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Injecte DATABASE_URL depuis .env dans la config Alembic
# Cela écrase la valeur sqlalchemy.url dans alembic.ini
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL non définie — vérifiez votre fichier .env")
config.set_main_option("sqlalchemy.url", database_url)

# ── Modèles SQLAlchemy ────────────────────────────────────────────────────────
# Tous les modèles doivent être importés ici pour qu'Alembic les détecte
# lors de la génération automatique de migrations (--autogenerate)
from app.database import Base
from app.models import user, room, equipment, reservation  # noqa: F401

target_metadata = Base.metadata


# ── Migrations offline (sans connexion DB active) ────────────────────────────
def run_migrations_offline() -> None:
    """
    Mode offline : génère le SQL sans connexion DB.
    Utile pour auditer les migrations avant de les appliquer.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


# ── Migrations online (connexion DB active) ───────────────────────────────────
def run_migrations_online() -> None:
    """
    Mode online : applique les migrations directement sur la DB.
    Mode par défaut lors d'un `alembic upgrade head`.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
