"""Prueba de regresión: GET /ucca/cycles debe existir y responder con auth deshabilitada."""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("AUTH_DISABLED", "true")
    from app.core.config import get_settings

    get_settings.cache_clear()
    from app.main import app

    yield TestClient(app)
    get_settings.cache_clear()


def test_list_cycles_without_token(client: TestClient):
    response = client.get("/ucca/cycles")
    assert response.status_code == 200
    assert response.json() == []
