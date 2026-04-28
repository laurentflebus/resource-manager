"""
Tests unitaires — reservation_service.py

Couvre :
- has_room_conflict()      : pas de conflit, conflit exact, chevauchements partiels
- has_equipment_conflict() : équipement introuvable, dans les limites de stock, stock épuisé
- serialize_reservation()  : salle, équipement, valeurs None
"""

from datetime import datetime, timedelta
import pytest

from app.models.reservation import Reservation
from app.models.room import Room
from app.models.equipment import Equipment
from app.services.reservation_service import (
    has_room_conflict,
    has_equipment_conflict,
    serialize_reservation,
)

# ── Helpers ──────────────────────────────────────────────────────────────────

def make_reservation(db, room_id=None, equipment_id=None, start_offset_h=1, duration_h=1):
    """Crée et persiste une réservation dans la DB de test."""
    now = datetime.now()
    r = Reservation(
        user_id=1,
        room_id=room_id,
        equipment_id=equipment_id,
        start_time=now + timedelta(hours=start_offset_h),
        end_time=now + timedelta(hours=start_offset_h + duration_h),
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def slot(start_offset_h=1, duration_h=1):
    """Retourne un tuple (start, end) pour une plage horaire future."""
    now = datetime.now()
    return (
        now + timedelta(hours=start_offset_h),
        now + timedelta(hours=start_offset_h + duration_h),
    )


# ── has_room_conflict ────────────────────────────────────────────────────────

class TestHasRoomConflict:

    def test_no_reservation_no_conflict(self, db, room):
        """Aucune réservation existante → pas de conflit."""
        start, end = slot(1, 2)
        assert has_room_conflict(db, room.id, start, end) is False

    def test_exact_overlap(self, db, room):
        """Réservation existante sur la même plage exacte → conflit."""
        make_reservation(db, room_id=room.id, start_offset_h=2, duration_h=2)
        start, end = slot(2, 2)
        assert has_room_conflict(db, room.id, start, end) is True

    def test_partial_overlap_start(self, db, room):
        """Nouvelle réservation commence pendant une existante → conflit."""
        make_reservation(db, room_id=room.id, start_offset_h=2, duration_h=2)
        start, end = slot(3, 2)  # commence à h+3, finit à h+5 (existante h+2 → h+4)
        assert has_room_conflict(db, room.id, start, end) is True

    def test_partial_overlap_end(self, db, room):
        """Nouvelle réservation se termine pendant une existante → conflit."""
        make_reservation(db, room_id=room.id, start_offset_h=3, duration_h=2)
        start, end = slot(2, 2)  # h+2 → h+4, existante h+3 → h+5
        assert has_room_conflict(db, room.id, start, end) is True

    def test_adjacent_no_conflict(self, db, room):
        """Réservation qui commence exactement quand l'autre finit → pas de conflit."""
        make_reservation(db, room_id=room.id, start_offset_h=1, duration_h=2)
        start, end = slot(3, 2)  # commence à h+3, l'autre finit à h+3
        assert has_room_conflict(db, room.id, start, end) is False

    def test_different_room_no_conflict(self, db, room):
        """Même plage horaire mais salle différente → pas de conflit."""
        make_reservation(db, room_id=room.id, start_offset_h=2, duration_h=2)
        start, end = slot(2, 2)
        assert has_room_conflict(db, room_id=999, start_time=start, end_time=end) is False

    def test_containing_overlap(self, db, room):
        """Nouvelle réservation englobe une existante → conflit."""
        make_reservation(db, room_id=room.id, start_offset_h=2, duration_h=1)
        start, end = slot(1, 4)  # englobe h+2 → h+3
        assert has_room_conflict(db, room.id, start, end) is True


# ── has_equipment_conflict ───────────────────────────────────────────────────

class TestHasEquipmentConflict:

    def test_equipment_not_found_blocks(self, db):
        """Équipement introuvable → bloqué par sécurité."""
        start, end = slot(1, 2)
        assert has_equipment_conflict(db, equipment_id=999, start_time=start, end_time=end) is True

    def test_no_reservation_no_conflict(self, db, equipment):
        """Aucune réservation existante → pas de conflit (quantity=2)."""
        start, end = slot(1, 2)
        assert has_equipment_conflict(db, equipment.id, start, end) is False

    def test_within_stock_no_conflict(self, db, equipment):
        """1 réservation existante sur quantity=2 → pas de conflit."""
        make_reservation(db, equipment_id=equipment.id, start_offset_h=2, duration_h=2)
        start, end = slot(2, 2)
        assert has_equipment_conflict(db, equipment.id, start, end) is False

    def test_stock_exhausted(self, db, equipment):
        """2 réservations existantes sur quantity=2 → conflit (stock épuisé)."""
        make_reservation(db, equipment_id=equipment.id, start_offset_h=2, duration_h=2)
        make_reservation(db, equipment_id=equipment.id, start_offset_h=2, duration_h=2)
        start, end = slot(2, 2)
        assert has_equipment_conflict(db, equipment.id, start, end) is True

    def test_non_overlapping_reuses_stock(self, db, equipment):
        """Réservations sur des plages non chevauchantes → stock disponible."""
        make_reservation(db, equipment_id=equipment.id, start_offset_h=1, duration_h=1)
        make_reservation(db, equipment_id=equipment.id, start_offset_h=1, duration_h=1)
        # 2 réservations existantes, mais sur h+5 → h+6 : pas de chevauchement
        start, end = slot(5, 1)
        assert has_equipment_conflict(db, equipment.id, start, end) is False

    def test_quantity_one_second_reservation_blocked(self, db):
        """Équipement quantity=1 : la 2e réservation sur la même plage est bloquée."""
        equip = Equipment(name="Unique", quantity=1)
        db.add(equip)
        db.commit()
        make_reservation(db, equipment_id=equip.id, start_offset_h=2, duration_h=2)
        start, end = slot(2, 2)
        assert has_equipment_conflict(db, equip.id, start, end) is True


# ── serialize_reservation ────────────────────────────────────────────────────

class TestSerializeReservation:

    def test_serialize_with_room(self, db, room):
        """Sérialisation d'une réservation de salle — room_name renseigné."""
        r = make_reservation(db, room_id=room.id)
        # Recharge avec relations pour simuler lazy='joined'
        db.refresh(r)
        result = serialize_reservation(r)

        assert result.id == r.id
        assert result.room_id == room.id
        assert result.room_name == "Salle A"
        assert result.equipment_name is None
        assert result.equipment_id is None

    def test_serialize_with_equipment(self, db, equipment):
        """Sérialisation d'une réservation d'équipement — equipment_name renseigné."""
        r = make_reservation(db, equipment_id=equipment.id)
        db.refresh(r)
        result = serialize_reservation(r)

        assert result.id == r.id
        assert result.equipment_id == equipment.id
        assert result.equipment_name == "Projecteur"
        assert result.room_name is None
        assert result.room_id is None

    def test_serialize_preserves_times(self, db, room):
        """Les dates de début et fin sont correctement préservées."""
        now = datetime.now()
        start = now + timedelta(hours=2)
        end = now + timedelta(hours=4)
        r = Reservation(user_id=1, room_id=room.id, start_time=start, end_time=end)
        db.add(r)
        db.commit()
        db.refresh(r)

        result = serialize_reservation(r)
        assert result.start_time == start
        assert result.end_time == end
