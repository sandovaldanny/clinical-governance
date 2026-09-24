"""Smoke: todos los listados de identity responden 200 con sesión vacía. Protege contra
funciones de servicio borradas por accidente (regresión real del 2026-09-24)."""
import pytest

from tests._fakes import FakeSession, cleanup, make_client


@pytest.fixture(autouse=True)
def _cleanup():
    yield
    cleanup()


@pytest.mark.parametrize(
    "path",
    [
        "/identity/users", "/identity/positions", "/identity/facilities", "/identity/professions",
        "/identity/roles", "/identity/permissions", "/identity/professionals", "/identity/catalogs",
        "/identity/catalogs?catalog_type=specialty", "/identity/me",
    ],
)
def test_list_endpoints_respond(monkeypatch, path):
    client = make_client(monkeypatch, FakeSession())
    response = client.get(path)
    assert response.status_code == 200, f"{path}: {response.text}"
