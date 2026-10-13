"""
Entrada para Vercel (Python Serverless Function).

La SPA llama al backend bajo el prefijo `/api` (en desarrollo lo quita el proxy de Vite). Aquí lo
quitamos nosotros antes de delegar en la app FastAPI real, que vive en `backend/app`.
"""
import os
import sys

BACKEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend")
sys.path.insert(0, os.path.normpath(BACKEND_DIR))

from app.main import app as fastapi_app  # noqa: E402

API_PREFIX = "/api"


async def app(scope, receive, send):
    if scope["type"] in ("http", "websocket"):
        path = scope.get("path", "")
        if path == API_PREFIX or path.startswith(API_PREFIX + "/"):
            scope = dict(scope)
            scope["path"] = path[len(API_PREFIX):] or "/"
            raw = scope.get("raw_path")
            if raw and raw.startswith(API_PREFIX.encode()):
                scope["raw_path"] = raw[len(API_PREFIX):] or b"/"
    await fastapi_app(scope, receive, send)
