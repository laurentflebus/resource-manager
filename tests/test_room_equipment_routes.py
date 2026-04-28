"""
Tests d'intégration — routes /rooms et /equipments

Couvre :
- GET    : accès authentifié obligatoire
- POST   : création admin, doublon, accès refusé user
- PUT    : mise à jour admin, 404, accès refusé user
- DELETE : suppression admin, 404, accès refusé user
"""


def auth(token):
    return {"Authorization": f"Bearer {token}"}


# ════════════════════════════════════════════════════════════════════════════
# ROOMS
# ════════════════════════════════════════════════════════════════════════════

class TestGetRooms:

    def test_authenticated_user_can_list(self, client, user_token):
        """Un utilisateur connecté peut lister les salles."""
        res = client.get("/rooms", headers=auth(user_token))
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    def test_unauthenticated_blocked(self, client):
        """Sans token → 401."""
        res = client.get("/rooms")
        assert res.status_code == 401


class TestCreateRoom:

    def test_admin_can_create(self, client, admin_token):
        """L'admin crée une salle → 201 avec les données correctes."""
        res = client.post("/rooms", json={
            "name": "Salle B", "capacity": 20, "location": "Bâtiment 2"
        }, headers=auth(admin_token))
        assert res.status_code == 201
        data = res.json()
        assert data["name"] == "Salle B"
        assert data["capacity"] == 20
        assert "id" in data

    def test_user_cannot_create(self, client, user_token):
        """Un user standard ne peut pas créer de salle → 403."""
        res = client.post("/rooms", json={
            "name": "Salle C", "capacity": 5, "location": "Bâtiment 3"
        }, headers=auth(user_token))
        assert res.status_code == 403

    def test_duplicate_name_blocked(self, client, admin_token):
        """Deux salles avec le même nom → 400 au second."""
        payload = {"name": "Salle D", "capacity": 10, "location": "RDC"}
        client.post("/rooms", json=payload, headers=auth(admin_token))
        res = client.post("/rooms", json=payload, headers=auth(admin_token))
        assert res.status_code == 400
        assert "existe déjà" in res.json()["detail"]

    def test_unauthenticated_blocked(self, client):
        """Sans token → 401."""
        res = client.post("/rooms", json={
            "name": "Salle E", "capacity": 5, "location": "RDC"
        })
        assert res.status_code == 401


class TestUpdateRoom:

    def _create_room(self, client, token):
        res = client.post("/rooms", json={
            "name": "Salle Update", "capacity": 10, "location": "RDC"
        }, headers=auth(token))
        return res.json()["id"]

    def test_admin_can_update(self, client, admin_token):
        """L'admin met à jour une salle → 200 avec les nouvelles valeurs."""
        rid = self._create_room(client, admin_token)
        res = client.put(f"/rooms/{rid}", json={"capacity": 50}, headers=auth(admin_token))
        assert res.status_code == 200
        assert res.json()["capacity"] == 50
        assert res.json()["name"] == "Salle Update"  # non modifié

    def test_user_cannot_update(self, client, admin_token, user_token):
        """Un user standard ne peut pas modifier → 403."""
        rid = self._create_room(client, admin_token)
        res = client.put(f"/rooms/{rid}", json={"capacity": 5}, headers=auth(user_token))
        assert res.status_code == 403

    def test_not_found(self, client, admin_token):
        """Salle inexistante → 404."""
        res = client.put("/rooms/9999", json={"capacity": 5}, headers=auth(admin_token))
        assert res.status_code == 404


class TestDeleteRoom:

    def _create_room(self, client, token):
        res = client.post("/rooms", json={
            "name": "Salle Delete", "capacity": 10, "location": "RDC"
        }, headers=auth(token))
        return res.json()["id"]

    def test_admin_can_delete(self, client, admin_token):
        """L'admin supprime une salle → 200."""
        rid = self._create_room(client, admin_token)
        res = client.delete(f"/rooms/{rid}", headers=auth(admin_token))
        assert res.status_code == 200
        assert "supprimée" in res.json()["message"]

    def test_deleted_room_not_in_list(self, client, admin_token):
        """Après suppression, la salle n'apparaît plus dans GET /rooms."""
        rid = self._create_room(client, admin_token)
        client.delete(f"/rooms/{rid}", headers=auth(admin_token))
        ids = [r["id"] for r in client.get("/rooms", headers=auth(admin_token)).json()]
        assert rid not in ids

    def test_user_cannot_delete(self, client, admin_token, user_token):
        """Un user standard ne peut pas supprimer → 403."""
        rid = self._create_room(client, admin_token)
        res = client.delete(f"/rooms/{rid}", headers=auth(user_token))
        assert res.status_code == 403

    def test_not_found(self, client, admin_token):
        """Salle inexistante → 404."""
        res = client.delete("/rooms/9999", headers=auth(admin_token))
        assert res.status_code == 404


# ════════════════════════════════════════════════════════════════════════════
# EQUIPMENTS
# ════════════════════════════════════════════════════════════════════════════

class TestGetEquipments:

    def test_authenticated_user_can_list(self, client, user_token):
        """Un utilisateur connecté peut lister les équipements."""
        res = client.get("/equipments", headers=auth(user_token))
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    def test_unauthenticated_blocked(self, client):
        """Sans token → 401."""
        res = client.get("/equipments")
        assert res.status_code == 401


class TestCreateEquipment:

    def test_admin_can_create(self, client, admin_token):
        """L'admin crée un équipement → 201 avec les données correctes."""
        res = client.post("/equipments", json={
            "name": "Écran 4K", "quantity": 3
        }, headers=auth(admin_token))
        assert res.status_code == 201
        data = res.json()
        assert data["name"] == "Écran 4K"
        assert data["quantity"] == 3
        assert "id" in data

    def test_default_quantity_is_one(self, client, admin_token):
        """Sans quantity dans le payload, la valeur par défaut est 1."""
        res = client.post("/equipments", json={
            "name": "Câble HDMI", "quantity": 1
        }, headers=auth(admin_token))
        assert res.status_code == 201
        assert res.json()["quantity"] == 1

    def test_user_cannot_create(self, client, user_token):
        """Un user standard ne peut pas créer un équipement → 403."""
        res = client.post("/equipments", json={
            "name": "Tablette", "quantity": 2
        }, headers=auth(user_token))
        assert res.status_code == 403

    def test_duplicate_name_blocked(self, client, admin_token):
        """Deux équipements avec le même nom → 400 au second."""
        payload = {"name": "Micro", "quantity": 2}
        client.post("/equipments", json=payload, headers=auth(admin_token))
        res = client.post("/equipments", json=payload, headers=auth(admin_token))
        assert res.status_code == 400
        assert "existe déjà" in res.json()["detail"]


class TestUpdateEquipment:

    def _create_equipment(self, client, token):
        res = client.post("/equipments", json={
            "name": "Équip Update", "quantity": 2
        }, headers=auth(token))
        return res.json()["id"]

    def test_admin_can_update(self, client, admin_token):
        """L'admin met à jour un équipement → 200 avec les nouvelles valeurs."""
        eid = self._create_equipment(client, admin_token)
        res = client.put(f"/equipments/{eid}", json={"quantity": 5}, headers=auth(admin_token))
        assert res.status_code == 200
        assert res.json()["quantity"] == 5
        assert res.json()["name"] == "Équip Update"  # non modifié

    def test_user_cannot_update(self, client, admin_token, user_token):
        """Un user standard ne peut pas modifier → 403."""
        eid = self._create_equipment(client, admin_token)
        res = client.put(f"/equipments/{eid}", json={"quantity": 1}, headers=auth(user_token))
        assert res.status_code == 403

    def test_not_found(self, client, admin_token):
        """Équipement inexistant → 404."""
        res = client.put("/equipments/9999", json={"quantity": 1}, headers=auth(admin_token))
        assert res.status_code == 404


class TestDeleteEquipment:

    def _create_equipment(self, client, token):
        res = client.post("/equipments", json={
            "name": "Équip Delete", "quantity": 1
        }, headers=auth(token))
        return res.json()["id"]

    def test_admin_can_delete(self, client, admin_token):
        """L'admin supprime un équipement → 200."""
        eid = self._create_equipment(client, admin_token)
        res = client.delete(f"/equipments/{eid}", headers=auth(admin_token))
        assert res.status_code == 200
        assert "supprimé" in res.json()["message"]

    def test_deleted_equipment_not_in_list(self, client, admin_token):
        """Après suppression, l'équipement n'apparaît plus dans GET /equipments."""
        eid = self._create_equipment(client, admin_token)
        client.delete(f"/equipments/{eid}", headers=auth(admin_token))
        ids = [e["id"] for e in client.get("/equipments", headers=auth(admin_token)).json()]
        assert eid not in ids

    def test_user_cannot_delete(self, client, admin_token, user_token):
        """Un user standard ne peut pas supprimer → 403."""
        eid = self._create_equipment(client, admin_token)
        res = client.delete(f"/equipments/{eid}", headers=auth(user_token))
        assert res.status_code == 403

    def test_not_found(self, client, admin_token):
        """Équipement inexistant → 404."""
        res = client.delete("/equipments/9999", headers=auth(admin_token))
        assert res.status_code == 404
