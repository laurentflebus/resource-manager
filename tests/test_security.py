"""
Tests unitaires — security.py

Couvre :
- hash_password / verify_password : hachage bcrypt
- create_access_token             : structure et contenu du JWT
- require_admin                   : autorisation par rôle
"""

import time
import pytest
from fastapi import HTTPException

from app.models.user import User
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    require_admin,
)


# ── Helpers ──────────────────────────────────────────────────────────────────

def make_user(role="user", email="test@test.com"):
    """Construit un objet User sans persister en DB."""
    u = User()
    u.id = 1
    u.email = email
    u.role = role
    u.password = hash_password("password123")
    return u


# ── hash_password / verify_password ─────────────────────────────────────────

class TestPassword:

    def test_hash_is_not_plaintext(self):
        """Le hash ne doit pas être identique au mot de passe en clair."""
        hashed = hash_password("secret")
        assert hashed != "secret"

    def test_hash_starts_with_bcrypt_prefix(self):
        """Un hash bcrypt commence toujours par $2b$."""
        hashed = hash_password("secret")
        assert hashed.startswith("$2b$")

    def test_verify_correct_password(self):
        """verify_password retourne True pour le bon mot de passe."""
        hashed = hash_password("correct")
        assert verify_password("correct", hashed) is True

    def test_verify_wrong_password(self):
        """verify_password retourne False pour un mauvais mot de passe."""
        hashed = hash_password("correct")
        assert verify_password("wrong", hashed) is False

    def test_two_hashes_are_different(self):
        """Deux hachages du même mot de passe produisent des valeurs différentes (salt)."""
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2

    def test_empty_password(self):
        """Un mot de passe vide peut être haché et vérifié."""
        hashed = hash_password("")
        assert verify_password("", hashed) is True
        assert verify_password("notempty", hashed) is False


# ── create_access_token ──────────────────────────────────────────────────────

class TestCreateAccessToken:

    def test_returns_string(self):
        """Le token retourné est une chaîne de caractères."""
        user = make_user()
        token = create_access_token(user)
        assert isinstance(token, str)

    def test_token_has_three_parts(self):
        """Un JWT valide contient exactement 3 parties séparées par des points."""
        user = make_user()
        token = create_access_token(user)
        parts = token.split(".")
        assert len(parts) == 3

    def test_token_contains_email(self):
        """Le payload du token contient l'email dans le claim 'sub'."""
        import base64, json
        user = make_user(email="laurent@test.com")
        token = create_access_token(user)
        payload_b64 = token.split(".")[1]
        # Ajoute le padding base64 si nécessaire
        payload_b64 += "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        assert payload["sub"] == "laurent@test.com"

    def test_token_contains_role(self):
        """Le payload du token contient le rôle de l'utilisateur."""
        import base64, json
        user = make_user(role="admin")
        token = create_access_token(user)
        payload_b64 = token.split(".")[1]
        payload_b64 += "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        assert payload["role"] == "admin"

    def test_token_has_expiry(self):
        """Le token contient un claim 'exp' dans le futur."""
        user = make_user()
        token = create_access_token(user)
        import base64, json
        payload_b64 = token.split(".")[1]
        payload_b64 += "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        assert "exp" in payload
        assert payload["exp"] > int(time.time())

    def test_token_has_iat(self):
        """Le token contient un claim 'iat' (issued-at)."""
        import base64, json
        user = make_user()
        token = create_access_token(user)
        payload_b64 = token.split(".")[1]
        payload_b64 += "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        assert "iat" in payload

    def test_different_users_get_different_tokens(self):
        """Deux utilisateurs différents obtiennent des tokens différents."""
        u1 = make_user(email="a@test.com")
        u2 = make_user(email="b@test.com")
        assert create_access_token(u1) != create_access_token(u2)


# ── require_admin ────────────────────────────────────────────────────────────

class TestRequireAdmin:

    def test_admin_passes(self):
        """Un utilisateur admin ne lève pas d'exception."""
        admin = make_user(role="admin")
        require_admin(admin)  # ne doit pas lever

    def test_user_raises_403(self):
        """Un utilisateur standard lève une HTTPException 403."""
        user = make_user(role="user")
        with pytest.raises(HTTPException) as exc_info:
            require_admin(user)
        assert exc_info.value.status_code == 403

    def test_unknown_role_raises_403(self):
        """Un rôle inconnu lève une HTTPException 403."""
        unknown = make_user(role="moderator")
        with pytest.raises(HTTPException) as exc_info:
            require_admin(unknown)
        assert exc_info.value.status_code == 403
