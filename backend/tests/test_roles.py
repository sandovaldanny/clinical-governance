"""Roles + matriz rol→permiso (M01 doc, tablas 5/6/8): editar un rol reemplaza sus permisos y
aplica a todos sus usuarios; System Administrator conserva siempre todos los permisos."""
import json
import uuid

import pytest

from tests._fakes import FakeSession, cleanup, make_client

PERMS = frozenset({"users.view", "roles.manage"})


@pytest.fixture(autouse=True)
def _cleanup():
    yield
    cleanup()


def _role(code="auditor", system=False):
    from app.domains.identity.models import AegisRole

    return AegisRole(id=uuid.uuid4(), code=code, name=code.title(), description="", is_system_defined=system, is_active=True)


def test_list_permissions_grouped_by_module(monkeypatch):
    from app.domains.identity.models import Permission

    rows = [
        Permission(id=uuid.uuid4(), code="ucca.view", module="ucca", name="ucca.view", description="Ver"),
        Permission(id=uuid.uuid4(), code="ucca.approve", module="ucca", name="ucca.approve", description="Aprobar"),
        Permission(id=uuid.uuid4(), code="users.manage", module="users", name="users.manage", description="Admin"),
    ]
    client = make_client(monkeypatch, FakeSession(scalars_results=[rows]), PERMS)
    r = client.get("/identity/permissions")
    assert r.status_code == 200, r.text
    modules = {g["module"]: [p["code"] for p in g["permissions"]] for g in r.json()}
    assert modules == {"ucca": ["ucca.view", "ucca.approve"], "users": ["users.manage"]}


def test_create_role_with_permissions(monkeypatch):
    from app.domains.identity.models import AegisRole, RolePermissionAssignment

    p1, p2 = uuid.uuid4(), uuid.uuid4()
    session = FakeSession(scalars_results=[[p1, p2], [], [p1, p2]])  # ids válidos; users; perm ids out
    client = make_client(monkeypatch, session, PERMS)
    r = client.post(
        "/identity/roles",
        json={"code": "external_auditor", "name": "External Auditor", "description": "Temporal", "permission_ids": [str(p1), str(p2)]},
    )
    assert r.status_code == 201, r.text
    role = next(o for o in session.added if isinstance(o, AegisRole))
    assert role.code == "external_auditor" and role.is_active is True
    assert {o.permission_id for o in session.added if isinstance(o, RolePermissionAssignment)} == {p1, p2}
    assert session.committed


def test_update_role_replaces_permissions_and_audits(monkeypatch):
    from app.domains.identity.models import RolePermissionAssignment

    role = _role("auditor")
    keep, drop, new = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    current = [
        RolePermissionAssignment(id=uuid.uuid4(), role_id=role.id, permission_id=keep),
        RolePermissionAssignment(id=uuid.uuid4(), role_id=role.id, permission_id=drop),
    ]
    # scalar #1: rol. scalars: #1 ids válidos, #2 asignaciones actuales, #3 user_count(ids), #4 perm ids (out)
    session = FakeSession(scalar_results=[role], scalars_results=[[keep, new], current, [], [keep, new]])
    client = make_client(monkeypatch, session, PERMS)
    r = client.patch(f"/identity/roles/{role.id}", json={"description": "Audita UCCA", "permission_ids": [str(keep), str(new)]})
    assert r.status_code == 200, r.text
    assert role.description == "Audita UCCA"
    assert current[1] in session.deleted and current[0] not in session.deleted
    assert any(isinstance(o, RolePermissionAssignment) and o.permission_id == new for o in session.added)
    _, params = next(e for e in session.executed if e[1] and e[1].get("action") == "update")
    diff = json.loads(params["new_values"])
    assert set(diff["permission_ids"]) == {str(keep), str(new)}


def test_system_administrator_keeps_all_permissions(monkeypatch):
    role = _role("system_administrator", system=True)
    session = FakeSession(scalar_results=[role, role], scalars_results=[[uuid.uuid4()]])
    client = make_client(monkeypatch, session, PERMS)
    r = client.patch(f"/identity/roles/{role.id}", json={"permission_ids": [str(uuid.uuid4())]})
    assert r.status_code == 409
    r2 = client.patch(f"/identity/roles/{role.id}", json={"is_active": False})
    assert r2.status_code == 409


def test_unknown_permission_id_rejected(monkeypatch):
    role = _role("auditor")
    session = FakeSession(scalar_results=[role], scalars_results=[[]])  # ningún id válido
    client = make_client(monkeypatch, session, PERMS)
    r = client.patch(f"/identity/roles/{role.id}", json={"permission_ids": [str(uuid.uuid4())]})
    assert r.status_code == 422
