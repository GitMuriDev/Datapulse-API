from fastapi import APIRouter

from app.api.v1.endpoints import user
from app.api.v1.endpoints import alert, application, auth, ingest, metric

api_router = APIRouter()

# Unificação das Controllers no Roteador Principal v1
api_router.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
api_router.include_router(user.router, prefix="/users", tags=["Usuários"])
api_router.include_router(
    application.router, prefix="/applications", tags=["Aplicações"]
)
api_router.include_router(metric.router, prefix="/metrics", tags=["Métricas & Analytics"])
api_router.include_router(alert.router, prefix="/alerts", tags=["Regras de Alerta & Incidentes"])
api_router.include_router(ingest.router, tags=["Ingestão de Telemetria"])