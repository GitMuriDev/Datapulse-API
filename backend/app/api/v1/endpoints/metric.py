from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models.metric import Metric
from app.models.user import User
from app.schemas.metric import (
    MetricCreate,
    MetricUpdate,
    MetricResponse,
    ApplicationPerformanceSummary,
    SlowestEndpointSummary,
)
from app.services import metric as metric_service
from app.services import application as application_service

router = APIRouter()

# CRUD
# 1. CREATE (Criar)
@router.post(
    "/application/{application_id}",
    response_model=MetricResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar nova métrica",
    description="Registra um novo evento de telemetria/métrica associado a uma aplicação específica.",
)
def create_metric(
    *,
    db: Session = Depends(deps.get_db),
    application_id: int,
    metric_in: MetricCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Metric:
    app = application_service.get_application_by_id(db, application_id=application_id)
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aplicação não encontrada.",
        )
    
    if app.user_id_user != current_user.id_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para registrar métricas nesta aplicação.",
        )

    return metric_service.create_metric(
        db=db, metric_in=metric_in, application_id=application_id
    )


# 2. READ (Listar)
@router.get(
    "/",
    response_model=List[MetricResponse],
    summary="Listar todas as métricas (Admin)",
    description="Retorna a lista paginada de todas as métricas gravadas no sistema.",
)
def get_metrics(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> List[Metric]:
    return metric_service.get_metrics(db, skip=skip, limit=limit)


# 3. UPDATE (Atualizar)
@router.put(
    "/{id_metric}",
    response_model=MetricResponse,
    summary="Atualizar métrica por ID",
    description="Atualiza os campos de uma métrica cadastrada.",
)
def update_metric_by_id(
    *,
    db: Session = Depends(deps.get_db),
    id_metric: int,
    metric_in: MetricUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Metric:
    metric = metric_service.get_metric_by_id(db, id_metric=id_metric)
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Métrica não encontrada.",
        )

    app = application_service.get_application_by_id(
        db, application_id=metric.application_id_application
    )
    if not app or app.user_id_user != current_user.id_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para alterar métricas desta aplicação.",
        )

    update_data = metric_in.model_dump(exclude_unset=True)
    return metric_service.update_metric_by_id(
        db, id_metric=id_metric, update_data=update_data
    )


# 4. DELETE (Deletar)
@router.delete(
    "/{metric_id}",
    response_model=MetricResponse,
    summary="Deletar métrica por ID",
    description="Remove uma métrica do sistema.",
)
def delete_metric(
    *,
    db: Session = Depends(deps.get_db),
    metric_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Metric:
    metric = metric_service.get_metric_by_id(db, id_metric=metric_id)
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Métrica não encontrada.",
        )

    app = application_service.get_application_by_id(
        db, application_id=metric.application_id_application
    )
    if not app or app.user_id_user != current_user.id_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para remover métricas desta aplicação.",
        )

    return metric_service.delete_metric(db, metric_id=metric_id)

# FIMCRUD

# Buscar por ID
@router.get(
    "/{id_metric}",
    response_model=MetricResponse,
    summary="Buscar métrica por ID",
    description="Retorna os detalhes de uma métrica específica pelo seu ID primário.",
)
def get_metric_by_id(
    id_metric: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Metric:
    metric = metric_service.get_metric_by_id(db, id_metric=id_metric)
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Métrica não encontrada.",
        )

    app = application_service.get_application_by_id(
        db, application_id=metric.application_id_application
    )
    if not app or app.user_id_user != current_user.id_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para acessar esta métrica.",
        )
    return metric


# Busca telemetrias de uma aplicação específica com filtro de janela de tempo
@router.get(
    "/application/{application_id}/series",
    response_model=List[MetricResponse],
    summary="Listar métricas da aplicação por intervalo",
    description="Retorna a série temporal de telemetrias filtrada por data inicial e final para gráficos de dashboard.",
)
def get_metrics_by_application(
    application_id: int,
    db: Session = Depends(deps.get_db),
    start_date: Optional[datetime] = Query(None, description="Data inicial no formato ISO8601"),
    end_date: Optional[datetime] = Query(None, description="Data final no formato ISO8601"),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> List[Metric]:
    app = application_service.get_application_by_id(db, application_id=application_id)
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aplicação não encontrada.",
        )
    if app.user_id_user != current_user.id_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para acessar os dados desta aplicação.",
        )

    return metric_service.get_metrics_by_application(
        db=db,
        application_id=application_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )


# Consolida KPIs vitais da aplicação
@router.get(
    "/application/{application_id}/summary",
    response_model=ApplicationPerformanceSummary,
    summary="Resumo de performance da aplicação (KPIs)",
    description="Retorna o Total de Requisições, Latência Média, Total de Erros (5xx) e Error Rate %.",
)
def get_application_performance_summary(
    application_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> dict:
    app = application_service.get_application_by_id(db, application_id=application_id)
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aplicação não encontrada.",
        )
    if app.user_id_user != current_user.id_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para acessar o resumo desta aplicação.",
        )

    return metric_service.get_application_performance_summary(
        db, application_id=application_id
    )


# Identifica os gargalos de performance (endpoints mais lentos) da aplicação
@router.get(
    "/application/{application_id}/slowest",
    response_model=List[SlowestEndpointSummary],
    summary="Endpoints mais lentos (Gargalos)",
    description="Identifica as rotas com maior latência média para diagnóstico de performance.",
)
def get_slowest_endpoints(
    application_id: int,
    db: Session = Depends(deps.get_db),
    limit: int = 5,
    current_user: User = Depends(deps.get_current_user),
) -> List[dict]:
    app = application_service.get_application_by_id(db, application_id=application_id)
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aplicação não encontrada.",
        )
    if app.user_id_user != current_user.id_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para acessar os dados desta aplicação.",
        )

    return metric_service.get_slowest_endpoints(
        db, application_id=application_id, limit=limit
    )