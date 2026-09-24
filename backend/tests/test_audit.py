"""
record_event debe serializar previous/new_values a JSON antes del bind: la inserción usa
text() y psycopg no adapta dict (regresión: 500 al desactivar usuarios / crear ciclos).
"""
import json

from app.core.audit import record_event


class _CapturingSession:
    def __init__(self):
        self.params = None

    def execute(self, _stmt, params):
        self.params = params


def test_record_event_serializes_json_values():
    db = _CapturingSession()
    record_event(
        db,
        actor_user_id="a",
        module="identity",
        entity_type="User",
        entity_id="u",
        action="deactivate",
        previous_values={"is_active": True},
        new_values={"is_active": False},
    )
    assert isinstance(db.params["previous_values"], str)
    assert json.loads(db.params["new_values"]) == {"is_active": False}


def test_record_event_keeps_null_values():
    db = _CapturingSession()
    record_event(db, actor_user_id="a", module="m", entity_type="E", entity_id="e", action="create")
    assert db.params["previous_values"] is None
    assert db.params["new_values"] is None
