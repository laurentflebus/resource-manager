"""
Script utilitaire — Création d'un compte administrateur.

Usage :
    python scripts/create_admin.py

Le script crée un utilisateur admin avec les identifiants définis ci-dessous
s'il n'existe pas encore en base.

À n'exécuter qu'une seule fois lors de l'initialisation du projet.
Les identifiants doivent être changés avant toute mise en production.
"""

import sys
import os

# Ajoute la racine du projet au PYTHONPATH pour les imports relatifs
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from app.database import SessionLocal
from app.models.user import User
from app.utils.security import hash_password

# ── Identifiants par défaut — À CHANGER avant usage en production ─────────────
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "admin123"
# ─────────────────────────────────────────────────────────────────────────────

db = SessionLocal()

try:
    existing = db.query(User).filter(User.email == ADMIN_EMAIL).first()
    if existing:
        print(f"⚠️  Un compte admin existe déjà pour {ADMIN_EMAIL}")
        sys.exit(0)

    admin = User(
        email=ADMIN_EMAIL,
        password=hash_password(ADMIN_PASSWORD),
        role="admin"
    )
    db.add(admin)
    db.commit()
    print(f"✅ Admin créé : {ADMIN_EMAIL}")

except Exception as e:
    db.rollback()
    print(f"❌ Erreur lors de la création de l'admin : {e}")
    sys.exit(1)

finally:
    db.close()
