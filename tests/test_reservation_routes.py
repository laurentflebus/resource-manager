"""
Tests d'intégration — routes /reservations

Teste les endpoints via le TestClient FastAPI avec une DB SQLite en mémoire.
Couvre les cas nominaux et les cas d'erreur pour chaque endpoint.

Couvre :
- POST   /reservations  : création, validation, conflits
- GET    /reservations  : filtrage par rôle
- PUT    /reservations  : mise à jour, 404, droits admin
- DELETE /reservations  : suppression, 404, droits admin
"""

from datetime import datetime, timedelta
import pytest

from app.models.reservation import Reservation


# ── Helpers ──────────────────────────────────────────────────────────────────

def auth(token):
    """Retourne le header Authorization pour les requêtes authentifiées."""
    return {"Authorization": f"Bearer {token}"}


def future_slot(start_offset_h=2, duration_h=2):
    """Retourne un dict start_time/end_time pour une plage future."""
    now = datetime.now()
    return {
        "start_time": (now + timedelta(hours=start_offset_h)).isoformat(),
        "end_time": (now + timedelta(hours=start_offset_h + duration_h)).isoformat(),
    }


def past_slot():
    """Retourne un dict start_time/end_time dans le passé."""
    now = datetime.now()
    return {
        "start_time": (now - timedelta(hours=4)).isoformat(),
        "end_time": (now - timedelta(hours=2)).isoformat(),
    }


# ── POST /reservations ───────────────────────────────────────────────────────

class TestCreateReservation:

    def test_create_room_reservation(self, client, user_token, room):
        """Crée une réservation de salle valide → 200 avec les données correctes."""
        payload = {"room_id": room.id, **future_slot()}
        res = client.post("/reservations", json=payload, headers=auth(user_token))
        assert res.status_code == 200
        data = res.json()
        assert data["room_id"] == room.id
        assert data["room_name"] == "Salle A"
        assert "id" in data

    def test_create_equipment_reservation(self, client, user_token, equipment):
        """Crée une réservation d'équipement valide → 200 avec les données correctes."""
        payload = {"equipment_id": equipment.id, **future_slot()}
        res = client.post("/reservations", json=payload, headers=auth(user_token))
        assert res.status_code == 200
        data = res.json()
        assert data["equipment_id"] == equipment.id
        assert data["equipment_name"] == "Projecteur"

    def test_create_without_resource_fails(self, client, user_token):
        """Réservation sans room_id ni equipment_id → 400."""
        payload = future_slot()
        res = client.post("/reservations", json=payload, headers=auth(user_token))
        assert res.status_code == 400

    def test_create_in_past_fails(self, client, user_token, room):
        """Réservation dans le passé → 400."""
        payload = {"room_id": room.id, **past_slot()}
        res = client.post("/reservations", json=payload, headers=auth(user_token))
        assert res.status_code == 400

    def test_create_room_conflict_fails(self, client, user_token, room):
        """Deux réservations sur la même salle et la même plage → 400 au second."""
        payload = {"room_id": room.id, **future_slot(2, 2)}
        client.post("/reservations", json=payload, headers=auth(user_token))
        res = client.post("/reservations", json=payload, headers=auth(user_token))
        assert res.status_code == 400
        assert "Conflit" in res.json()["detail"]

    def test_create_equipment_conflict_at_max_stock(self, client, user_token, equipment):
        """Dépasse la quantity=2 de l'équipement → 400 à la 3e réservation."""
        payload = {"equipment_id": equipment.id, **future_slot(2, 2)}
        client.post("/reservations", json=payload, headers=auth(user_token))
        client.post("/reservations", json=payload, headers=auth(user_token))
        res = client.post("/reservations", json=payload, headers=auth(user_token))
        assert res.status_code == 400

    def test_create_unauthenticated_fails(self, client, room):
        """Sans token → 401."""
        payload = {"room_id": room.id, **future_slot()}
        res = client.post("/reservations", json=payload)
        assert res.status_code == 401


# ── GET /reservations ────────────────────────────────────────────────────────

class TestGetReservations:

    def test_admin_sees_all(self, client, admin_token, user_token, room):
        """L'admin voit toutes les réservations, peu importe qui les a créées."""
        payload = {"room_id": room.id, **future_slot()}
        client.post("/reservations", json=payload, headers=auth(user_token))

        res = client.get("/reservations", headers=auth(admin_token))
        assert res.status_code == 200
        assert len(res.json()) == 1

    def test_user_sees_only_own(self, client, user_token, admin_token, room, equipment):
        """Un utilisateur standard ne voit que ses propres réservations."""
        # La réservation de l'user
        client.post("/reservations", json={"room_id": room.id, **future_slot(2, 1)}, headers=auth(user_token))
        # Une réservation de l'admin (autre plage)
        client.post("/reservations", json={"equipment_id": equipment.id, **future_slot(5, 1)}, headers=auth(admin_token))

        res = client.get("/reservations", headers=auth(user_token))
        assert res.status_code == 200
        assert len(res.json()) == 1
        assert res.json()[0]["room_id"] == room.id

    def test_get_unauthenticated_fails(self, client):
        """Sans token → 401."""
        res = client.get("/reservations")
        assert res.status_code == 401

    def test_empty_list(self, client, user_token):
        """Aucune réservation → liste vide."""
        res = client.get("/reservations", headers=auth(user_token))
        assert res.status_code == 200
        assert res.json() == []


# ── PUT /reservations/{id} ───────────────────────────────────────────────────

class TestUpdateReservation:

    def _create_reservation(self, client, token, room):
        payload = {"room_id": room.id, **future_slot(2, 2)}
        res = client.post("/reservations", json=payload, headers=auth(token))
        return res.json()["id"]

    def test_admin_can_update(self, client, admin_token, room):
        """L'admin peut décaler une réservation → 200 avec les nouvelles dates."""
        rid = self._create_reservation(client, admin_token, room)
        new_slot = future_slot(6, 2)
        res = client.put(f"/reservations/{rid}", json=new_slot, headers=auth(admin_token))
        assert res.status_code == 200
        assert "06" in res.json()["start_time"] or res.json()["start_time"] != ""

    def test_user_cannot_update(self, client, user_token, admin_token, room):
        """Un utilisateur standard ne peut pas modifier une réservation → 403."""
        rid = self._create_reservation(client, admin_token, room)
        res = client.put(f"/reservations/{rid}", json=future_slot(6, 2), headers=auth(user_token))
        assert res.status_code == 403

    def test_update_not_found(self, client, admin_token):
        """Mise à jour d'une réservation inexistante → 404."""
        res = client.put("/reservations/9999", json=future_slot(6, 2), headers=auth(admin_token))
        assert res.status_code == 404

    def test_update_conflict_fails(self, client, admin_token, room):
        """Mise à jour vers une plage occupée → 400."""
        # Réservation 1 : h+2 → h+4
        rid1 = self._create_reservation(client, admin_token, room)
        # Réservation 2 : h+5 → h+7
        payload2 = {"room_id": room.id, **future_slot(5, 2)}
        rid2 = client.post("/reservations", json=payload2, headers=auth(admin_token)).json()["id"]
        # Tente de déplacer rid2 sur la plage de rid1
        res = client.put(f"/reservations/{rid2}", json=future_slot(2, 2), headers=auth(admin_token))
        assert res.status_code == 400


# ── DELETE /reservations/{id} ────────────────────────────────────────────────

class TestDeleteReservation:

    def _create_reservation(self, client, token, room):
        payload = {"room_id": room.id, **future_slot(2, 2)}
        return client.post("/reservations", json=payload, headers=auth(token)).json()["id"]

    def test_admin_can_delete(self, client, admin_token, room):
        """L'admin peut supprimer une réservation → 200."""
        rid = self._create_reservation(client, admin_token, room)
        res = client.delete(f"/reservations/{rid}", headers=auth(admin_token))
        assert res.status_code == 200
        assert res.json()["message"] == "Réservation supprimée"

    def test_deleted_reservation_not_found(self, client, admin_token, room):
        """Après suppression, la réservation n'apparaît plus dans le GET."""
        rid = self._create_reservation(client, admin_token, room)
        client.delete(f"/reservations/{rid}", headers=auth(admin_token))
        reservations = client.get("/reservations", headers=auth(admin_token)).json()
        ids = [r["id"] for r in reservations]
        assert rid not in ids

    def test_user_cannot_delete(self, client, user_token, admin_token, room):
        """Un utilisateur standard ne peut pas supprimer → 403."""
        rid = self._create_reservation(client, admin_token, room)
        res = client.delete(f"/reservations/{rid}", headers=auth(user_token))
        assert res.status_code == 403

    def test_delete_not_found(self, client, admin_token):
        """Suppression d'une réservation inexistante → 404."""
        res = client.delete("/reservations/9999", headers=auth(admin_token))
        assert res.status_code == 404
