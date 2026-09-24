from fastapi import FastAPI

from app.api import api_router

app = FastAPI(
    title="AEGIS — Clinical Governance Platform",
    description="Arquetipo técnico. Ver docs/AEGIS_Arquitectura_Tecnica.md para el diseño completo.",
    version="0.1.0",
)

app.include_router(api_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
