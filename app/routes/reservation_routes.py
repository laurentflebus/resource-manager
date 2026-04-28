"""
Routes REST pour les réservations.

Endpoints :
    POST   /reservations       Crée une réservation (authentifié)
    GET    /reservations       Liste les réservations (admin : toutes, user : les siennes)
    PUT    /reservations/{id}  Met à jour une réservation (admin uniquement)
    DELETE /reservations/{id}  Supprime une réservation (admin uniquement)
"""

from math import ceil
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.reservation import Reservation
from app.models.user import User
from app.schemas.reservation import ReservationCreate, ReservationResponse, ReservationUpdate, PaginatedResponse
from app.services.reservation_service import has_room_conflict, has_equipment_conflict, serialize_reservation
from app.utils.security import get_current_user, require_admin

router = APIRouter()


@router.post("/reservations", response_model=ReservationResponse)
def create_reservation(
    reservation: ReservationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crée une nouvelle réservation pour une salle ou un équipement.

    Validations :
    - La date de début ne peut pas être dans le passé.
    - Exactement une ressource doit être spécifiée (salle OU équipement).
    - Aucun chevauchement avec une réservation existante sur la même ressource.
    """
    if reservation.start_time < datetime.now():
        raise HTTPException(status_code=400, detail="Impossible de réserver pour une date passée.")

    if reservation.room_id is None and reservation.equipment_id is None:
        raise HTTPException(status_code=400, detail="Vous devez spécifier au moins une salle ou un équipement.")

    if reservation.room_id and has_room_conflict(db, reservation.room_id, reservation.start_time, reservation.end_time):
        raise HTTPException(status_code=400, detail="Conflit : la salle est déjà réservée sur cette période.")

    if reservation.equipment_id and has_equipment_conflict(db, reservation.equipment_id, reservation.start_time, reservation.end_time):
        raise HTTPException(status_code=400, detail="Conflit : le matériel n'est pas disponible sur cette période.")

    db_reservation = Reservation(
        user_id=current_user.id,
        room_id=reservation.room_id,
        equipment_id=reservation.equipment_id,
        start_time=reservation.start_time,
        end_time=reservation.end_time
    )
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    return serialize_reservation(db_reservation)


@router.get("/reservations", response_model=PaginatedResponse)
def get_reservations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(default=1, ge=1, description="Numéro de page (commence à 1)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Nombre d'éléments par page (max 100)")
):
    """
    Retourne une page de réservations avec métadonnées de pagination.

    - Admin : toutes les réservations.
    - Utilisateur standard : uniquement ses propres réservations.

    Paramètres de pagination :
    - page      : numéro de page, commence à 1 (défaut : 1)
    - page_size : éléments par page, entre 1 et 100 (défaut : 20)

    Exemple : GET /reservations?page=2&page_size=10
    """
    query = db.query(Reservation)
    if current_user.role != "admin":
        query = query.filter(Reservation.user_id == current_user.id)

    # Compte total avant pagination — nécessaire pour les métadonnées
    total = query.count()

    # Applique la pagination avec tri par date de début (plus récent en premier)
    reservations = (
        query
        .order_by(Reservation.start_time.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return PaginatedResponse(
        items=[serialize_reservation(r) for r in reservations],
        total=total,
        page=page,
        page_size=page_size,
        pages=ceil(total / page_size) if total > 0 else 1
    )


@router.put("/reservations/{id}", response_model=ReservationResponse)
def update_reservation(
    id: int,
    payload: ReservationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Met à jour les dates (et optionnellement la ressource) d'une réservation existante.

    Réservé aux admins. Vérifie les conflits après mise à jour.
    Si un champ n'est pas fourni dans le payload, la valeur existante est conservée.
    """
    require_admin(current_user)

    reservation = db.query(Reservation).filter(Reservation.id == id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Réservation introuvable")

    # Applique les valeurs du payload ou conserve les valeurs existantes
    start = payload.start_time or reservation.start_time
    end = payload.end_time or reservation.end_time
    room_id = payload.room_id if payload.room_id is not None else reservation.room_id
    equipment_id = payload.equipment_id if payload.equipment_id is not None else reservation.equipment_id

    if room_id and has_room_conflict(db, room_id, start, end):
        raise HTTPException(status_code=400, detail="Conflit : la salle est déjà réservée sur cette période.")

    if equipment_id and has_equipment_conflict(db, equipment_id, start, end):
        raise HTTPException(status_code=400, detail="Conflit : le matériel n'est pas disponible sur cette période.")

    reservation.start_time = start
    reservation.end_time = end
    db.commit()
    db.refresh(reservation)
    return serialize_reservation(reservation)


@router.delete("/reservations/{id}")
def delete_reservation(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Supprime une réservation par son identifiant.

    Réservé aux admins. Retourne une 404 si la réservation n'existe pas.
    """
    require_admin(current_user)

    reservation = db.query(Reservation).filter(Reservation.id == id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Réservation introuvable")

    db.delete(reservation)
    db.commit()
    return {"message": "Réservation supprimée"}
