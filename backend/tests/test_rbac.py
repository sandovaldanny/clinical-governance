"""
Prueba de referencia: un usuario sin el permiso requerido debe ser rechazado por el middleware
de autorización, no por lógica ad hoc dentro del router del módulo.

La prueba fuerza AUTH_DISABLED=false para no depender del .env local del desarrollador
(el bypass de desarrollo devolvería siempre al usuario sin validar permisos).
"""
from fastapi import HTTPException
import pytest

from app.core.config import get_settings
from app.core.deps import CurrentUser
from app.core.rbac import require_permission


@pytest.fixture(autouse=True)
def _auth_enabled(monkeypatch):
    monkeypatch.setenv("AUTH_DISABLED", "false")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def _user_with(permissions: set[str]) -> CurrentUser:
    return CurrentUser(
        id="00000000-0000-0000-0000-000000000001",
        email="test@alkalma.local",
        facility_ids=["f1"],
        is_corporate=False,
        effective_permissions=permissions,
    )


def test_require_permission_allows_when_present():
    dependency = require_permission("ucca.create")
    user = _user_with({"ucca.create"})
    assert dependency(current_user=user) is user


def test_require_permission_rejects_when_missing():
    dependency = require_permission("ucca.approve")
    user = _user_with({"ucca.create"})
    with pytest.raises(HTTPException) as exc_info:
        dependency(current_user=user)
    assert exc_info.value.status_code == 403
