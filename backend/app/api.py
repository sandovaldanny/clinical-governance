"""
Punto único de registro de routers. Al agregar un módulo nuevo, se agrega su router aquí — este
es el único archivo transversal que un desarrollador de módulo necesita tocar fuera de su propia
carpeta de dominio.
"""
from fastapi import APIRouter

from app.domains.governance.ucca.router import router as ucca_router
from app.domains.identity.router import router as identity_router

api_router = APIRouter()
api_router.include_router(identity_router)
api_router.include_router(ucca_router)
