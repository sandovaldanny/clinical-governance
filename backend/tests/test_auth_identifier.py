"""Login por identificador: correo completo o solo la parte antes de la @ (p. ej. `admin`)."""
from app.core.security import hash_password
from app.domains.identity import service
from app.domains.identity.models import User
from tests._fakes import FakeSession


def _user() -> User:
    return User(email="admin@alkalma.health", full_name="Admin", hashed_password=hash_password("admin"), is_active=True)


def test_authenticate_accepts_short_identifier():
    db = FakeSession(scalar_results=[_user()])
    assert service.authenticate(db, identifier="admin", password="admin") is not None


def test_authenticate_accepts_full_email():
    db = FakeSession(scalar_results=[_user()])
    assert service.authenticate(db, identifier="admin@alkalma.health", password="admin") is not None


def test_authenticate_rejects_wrong_password():
    db = FakeSession(scalar_results=[_user()])
    assert service.authenticate(db, identifier="admin", password="nope") is None


def test_authenticate_unknown_identifier():
    db = FakeSession(scalar_results=[None])
    assert service.authenticate(db, identifier="ghost", password="admin") is None
