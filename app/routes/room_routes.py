"""
Routes REST pour les salles.

Endpoints :
    GET    /rooms        Liste toutes les salles (authentifié)
    POST   /rooms        Crée une salle (admin uniquement)
    PUT    /rooms/{id}   Modifie une salle (admin uniquement)
    DELETE /rooms/{id}   Supprime une salle (admin uniquement)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.room import Room
from app.models.user import User
from app.schemas.room import RoomCreate, RoomUpdate, RoomResponse
from app.utils.security import get_current_user, require_admin

router = APIRouter()


@router.get("/rooms", response_model=list[RoomResponse])
def get_rooms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retourne la liste de toutes les salles.

    Accessible à tout utilisateur authentifié — nécessaire pour
    alimenter le sélecteur de salle dans ReservationModal.
    """
    return db.query(Room).all()


@router.post("/rooms", response_model=RoomResponse, status_code=201)
def create_room(
    room: RoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crée une nouvelle salle.

    Réservé aux admins. Retourne une 400 si une salle du même nom existe déjà.
    """
    require_admin(current_user)

    existing = db.query(Room).filter(Room.name == room.name).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Une salle nommée '{room.name}' existe déjà.")

    db_room = Room(name=room.name, capacity=room.capacity, location=room.location)
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room


@router.put("/rooms/{id}", response_model=RoomResponse)
def update_room(
    id: int,
    payload: RoomUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Met à jour les informations d'une salle existante.

    Réservé aux admins. Seuls les champs fournis sont mis à jour.
    Retourne une 404 si la salle n'existe pas.
    """
    require_admin(current_user)

    room = db.query(Room).filter(Room.id == id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Salle introuvable.")

    if payload.name is not None:
        room.name = payload.name
    if payload.capacity is not None:
        room.capacity = payload.capacity
    if payload.location is not None:
        room.location = payload.location

    db.commit()
    db.refresh(room)
    return room


@router.delete("/rooms/{id}")
def delete_room(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Supprime une salle par son identifiant.

    Réservé aux admins. Retourne une 404 si la salle n'existe pas.
    """
    require_admin(current_user)

    room = db.query(Room).filter(Room.id == id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Salle introuvable.")

    db.delete(room)
    db.commit()
    return {"message": f"Salle '{room.name}' supprimée."}
