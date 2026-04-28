"""
Routes REST pour les équipements.

Endpoints :
    GET    /equipments        Liste tous les équipements (authentifié)
    POST   /equipments        Crée un équipement (admin uniquement)
    PUT    /equipments/{id}   Modifie un équipement (admin uniquement)
    DELETE /equipments/{id}   Supprime un équipement (admin uniquement)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.equipment import Equipment
from app.models.user import User
from app.schemas.equipment import EquipmentCreate, EquipmentUpdate, EquipmentResponse
from app.utils.security import get_current_user, require_admin

router = APIRouter()


@router.get("/equipments", response_model=list[EquipmentResponse])
def get_equipment(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retourne la liste de tous les équipements.

    Accessible à tout utilisateur authentifié — nécessaire pour
    alimenter le sélecteur d'équipement dans ReservationModal.
    """
    return db.query(Equipment).all()


@router.post("/equipments", response_model=EquipmentResponse, status_code=201)
def create_equipment(
    equipment: EquipmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crée un nouvel équipement.

    Réservé aux admins. La quantité détermine combien de réservations
    simultanées sont autorisées (voir has_equipment_conflict dans reservation_service).
    Retourne une 400 si un équipement du même nom existe déjà.
    """
    require_admin(current_user)

    existing = db.query(Equipment).filter(Equipment.name == equipment.name).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Un équipement nommé '{equipment.name}' existe déjà.")

    db_equipment = Equipment(name=equipment.name, quantity=equipment.quantity)
    db.add(db_equipment)
    db.commit()
    db.refresh(db_equipment)
    return db_equipment


@router.put("/equipments/{id}", response_model=EquipmentResponse)
def update_equipment(
    id: int,
    payload: EquipmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Met à jour un équipement existant.

    Réservé aux admins. Seuls les champs fournis sont mis à jour.
    Retourne une 404 si l'équipement n'existe pas.
    """
    require_admin(current_user)

    equipment = db.query(Equipment).filter(Equipment.id == id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Équipement introuvable.")

    if payload.name is not None:
        equipment.name = payload.name
    if payload.quantity is not None:
        equipment.quantity = payload.quantity

    db.commit()
    db.refresh(equipment)
    return equipment


@router.delete("/equipments/{id}")
def delete_equipment(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Supprime un équipement par son identifiant.

    Réservé aux admins. Retourne une 404 si l'équipement n'existe pas.
    """
    require_admin(current_user)

    equipment = db.query(Equipment).filter(Equipment.id == id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Équipement introuvable.")

    db.delete(equipment)
    db.commit()
    return {"message": f"Équipement '{equipment.name}' supprimé."}
