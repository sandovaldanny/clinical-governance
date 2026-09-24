"""Dobles mínimos de sesión SQLAlchemy para probar routers sin Postgres."""
from __future__ import annotations

DEV_USER_ID = "00000000-0000-0000-0000-000000000001"


class Scalars:
    def __init__(self, rows):
        self._rows = list(rows)

    def all(self):
        return self._rows

    def first(self):
        return self._rows[0] if self._rows else None


class Rows:
    def __init__(self, rows):
        self._rows = list(rows)

    def all(self):
        return self._rows


class FakeSession:
    """`scalar_results` se consume en orden (uno por llamada a .scalar()); cuando se agota
    devuelve None. `scalars_results` igual para .scalars(); `execute_rows` para .execute().all()."""

    def __init__(self, *, scalar_results=(), scalars_results=(), execute_rows=()):
        self._scalar = list(scalar_results)
        self._scalars = list(scalars_results)
        self._execute_rows = list(execute_rows)
        self.added: list = []
        self.deleted: list = []
        self.executed: list = []
        self.committed = False

    def scalar(self, *_a, **_k):
        return self._scalar.pop(0) if self._scalar else None

    def scalars(self, *_a, **_k):
        return Scalars(self._scalars.pop(0) if self._scalars else [])

    def execute(self, stmt, params=None):
        self.executed.append((stmt, params))
        return Rows(self._execute_rows.pop(0) if self._execute_rows else [])

    def add(self, obj):
        self.added.append(obj)

    def delete(self, obj):
        self.deleted.append(obj)

    def flush(self):
        import uuid

        for obj in self.added:
            if getattr(obj, "id", None) is None:
                obj.id = uuid.uuid4()

    def commit(self):
        self.committed = True

    def refresh(self, *_a, **_k):
        return None

    def close(self):
        return None


def make_client(monkeypatch, session, permissions=frozenset({"users.manage", "users.view"})):
    """TestClient con AUTH_DISABLED y el usuario dev fijo con los permisos dados."""
    monkeypatch.setenv("AUTH_DISABLED", "true")
    from fastapi.testclient import TestClient

    from app.core import deps
    from app.core.config import get_settings
    from app.core.database import get_db
    from app.main import app

    get_settings.cache_clear()

    def _fake_db():
        yield session

    app.dependency_overrides[get_db] = _fake_db
    monkeypatch.setattr(
        deps,
        "_dev_bypass_user",
        lambda db: deps.CurrentUser(
            id=DEV_USER_ID, email="dev@local", facility_ids=[], is_corporate=True,
            effective_permissions=set(permissions),
        ),
    )
    return TestClient(app)


def cleanup():
    from app.core.config import get_settings
    from app.main import app

    app.dependency_overrides.clear()
    get_settings.cache_clear()
