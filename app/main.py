"""
Point d'entrée de l'application FastAPI — Resource Manager.

Initialise l'application, enregistre les middlewares et monte les routers.

Note : la création des tables est gérée par Alembic (alembic upgrade head).
Ne pas utiliser Base.metadata.create_all() ici en production.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models import *  # noqa: F401,F403 — nécessaire pour Alembic
from app.routes import room_routes, reservation_routes, equipment_routes, auth_routes

app = FastAPI(
    title="Resource Manager API",
    description="API de gestion des réservations de salles et équipements.",
    version="1.0.0"
)

# ── Middlewares ──────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ── Routers ──────────────────────────────────────────────────────────────────
app.include_router(auth_routes.router)
app.include_router(room_routes.router)
app.include_router(reservation_routes.router)
app.include_router(equipment_routes.router)


@app.get("/", tags=["root"])
def root():
    """Vérifie que l'API est en ligne."""
    return {"message": "API Resource Manager running 🚀"}


@app.get("/health", tags=["root"])
def health():
    """Health check pour load balancer ou monitoring."""
    return {"status": "ok"}
