"""
Prueba de regresión: GET /ucca/cycles debe existir y responder 200 con auth deshabilitada.

No toca Postgres: se sustituye la sesión de base de datos por un doble y se aísla el servicio,
de modo que la prueba sea determinista aunque el desarrollador tenga datos seed locales.
"""
import pytest
from fastapi.testclient import TestClient


class _FakeSession:
    """Sesión mínima: el bypass de desarrollo consulta el admin (None -> usuario dev) y
    set_tenant_context ejecuta SET LOCAL (ignorado)."""

    def scalar(self, *_args, **_kwargs):
        return None

    def execute(self, *_args, **_kwargs):
        return None

    def close(self) -> None:
        return None


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("AUTH_DISABLED", "true")
    from app.core.config import get_settings

    get_settings.cache_clear()

    from app.core.database import get_db
    from app.domains.governance.ucca import service
    from app.main import app

    def _fake_db():
        yield _FakeSession()

    app.dependency_overrides[get_db] = _fake_db
    monkeypatch.setattr(service, "list_cycles", lambda db: [])

    yield TestClient(app)

    app.dependency_overrides.clear()
    get_settings.cache_clear()


def test_list_cycles_without_token(client: TestClient):
    response = client.get("/ucca/cycles")
    assert response.status_code == 200
    assert response.json() == []
