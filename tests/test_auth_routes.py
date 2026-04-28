"""
Tests d'intégration — routes /auth

Couvre :
- POST /auth/register : inscription valide, email dupliqué
- POST /auth/login    : connexion valide, mauvais mot de passe, utilisateur inconnu
"""


class TestRegister:

    def test_register_success(self, client):
        """Inscription avec des identifiants valides → 201 avec id et email."""
        res = client.post("/auth/register", json={
            "email": "nouveau@test.com",
            "password": "password123"
        })
        assert res.status_code == 201
        data = res.json()
        assert data["email"] == "nouveau@test.com"
        assert data["role"] == "user"
        assert "id" in data
        assert "password" not in data  # le hash ne doit jamais être exposé

    def test_register_duplicate_email(self, client):
        """Deux inscriptions avec le même email → 400 au second."""
        payload = {"email": "double@test.com", "password": "password123"}
        client.post("/auth/register", json=payload)
        res = client.post("/auth/register", json=payload)
        assert res.status_code == 400
        assert "already registered" in res.json()["detail"]


class TestLogin:

    def test_login_success(self, client, user):
        """Connexion avec les bons identifiants → token JWT retourné."""
        res = client.post("/auth/login", data={
            "username": user.email,
            "password": "password123"
        })
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        # Vérifie que c'est bien un JWT (3 parties)
        assert len(data["access_token"].split(".")) == 3

    def test_login_wrong_password(self, client, user):
        """Mauvais mot de passe → 401."""
        res = client.post("/auth/login", data={
            "username": user.email,
            "password": "wrong"
        })
        assert res.status_code == 401

    def test_login_unknown_email(self, client):
        """Email inconnu → 401."""
        res = client.post("/auth/login", data={
            "username": "ghost@test.com",
            "password": "password123"
        })
        assert res.status_code == 401

    def test_login_populates_role_in_token(self, client, admin):
        """Le token d'un admin contient bien role='admin'."""
        import base64, json
        res = client.post("/auth/login", data={
            "username": admin.email,
            "password": "admin123"
        })
        token = res.json()["access_token"]
        payload_b64 = token.split(".")[1]
        payload_b64 += "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        assert payload["role"] == "admin"
