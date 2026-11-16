from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.metric import MetricCreate, MetricResponse
from app.services import application as application_service
from app.services import metric as metric_service

router = APIRouter()


@router.post(
    "/ingest",
    response_model=MetricResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingestão de métricas em tempo real (SDK/Agentes)",
    description="Endpoint público de alta performance para envio de telemetria. Autentica a aplicação via header X-API-Key.",
)
def ingest_metric(
    *,
    db: Session = Depends(deps.get_db),
    metric_in: MetricCreate,
    x_api_key: str = Header(..., alias="X-API-Key", description="API Key da aplicação consumidora"),
) -> MetricResponse:
    # 1. Valida se a API Key existe no banco de dados
    app = application_service.get_application_by_key(db, api_key=x_api_key)
    if not app:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida ou aplicação não encontrada.",
        )

    # 2. Grava a métrica associando-a à aplicação identificada
    return metric_service.create_metric(
        db=db, metric_in=metric_in, application_id=app.id_application
    )