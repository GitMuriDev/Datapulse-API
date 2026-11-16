from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.metric import Metric
from app.schemas.metric import MetricCreate
from sqlalchemy import func

# CRUD
# 1. CREATE (Criar)
def create_metric(
        db: Session, metric_in: MetricCreate, application_id: int
) -> Metric:
    db_metric = Metric(
        endpoint=metric_in.endpoint,
        method=metric_in.method,
        status_code=metric_in.status_code,
        latency_ms=metric_in.latency_ms,
        application_id_application=application_id
    )
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return db_metric


# 2. READ (Listar)
def get_metrics(db: Session, skip: int = 0, limit: int = 100) -> list[Metric]:
    return db.query(Metric).offset(skip).limit(limit).all()


# 3. UPDATE (Atualizar)
def update_metric_by_id(db: Session, id_metric: int, update_data: dict) -> Optional[Metric]:
    db_metric = get_metric_by_id(db, id_metric=id_metric)
    if not db_metric:
        return None

    for field, value in update_data.items():
        # Protege o ID, a chave estrangeira e a data do evento de serem sobrescritos
        if field in ["id_metric", "application_id_application", "timestamp"]:
            continue
        if hasattr(db_metric, field) and value is not None:
            setattr(db_metric, field, value)

    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return db_metric


# 4. DELETE (Deletar)
def delete_metric(db: Session, metric_id: int) -> Optional[Metric]:
    db_metric = get_metric_by_id(db, metric_id=metric_id)
    if not db_metric:
        return None

    db.delete(db_metric)
    db.commit()
    return db_metric

# FIMCRUD

# Buscar por ID
def get_metric_by_id(db: Session, id_metric: int) -> Optional[Metric]:
    return db.query(Metric).filter(Metric.id_metric == id_metric).first()


# Busca telemetrias de uma aplicação específica, permitindo filtrar por janela de tempo
# Essencial para gráficos de linha temporal no Dashboard
def get_metrics_by_application(
    db: Session,
    application_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Metric]:
    query = db.query(Metric).filter(Metric.application_id_application == application_id)
    
    if start_date:
        query = query.filter(Metric.timestamp >= start_date)
    if end_date:
        query = query.filter(Metric.timestamp <= end_date)
        
    return query.order_by(Metric.timestamp.desc()).offset(skip).limit(limit).all()


#Consolida KPIs vitais da aplicação:
def get_application_performance_summary(
    db: Session, application_id: int
) -> dict:
    # 1. Total de requisições registradas
    total_requests = (
        db.query(func.count(Metric.id_metric))
        .filter(Metric.application_id_application == application_id)
        .scalar() or 0
    )
    # 2. Latência média (tempo de resposta em ms)
    avg_latency = (
        db.query(func.avg(Metric.latency_ms))
        .filter(Metric.application_id_application == application_id)
        .scalar() or 0.0
    )
    # 3. Total de erros de servidor (status >= 500)
    total_errors = (
        db.query(func.count(Metric.id_metric))
        .filter(
            Metric.application_id_application == application_id,
            Metric.status_code >= 500
        )
        .scalar() or 0
    )

    # Cálculo percentual de taxa de erro (Error Rate)
    error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0.0

    return {
        "application_id": application_id,
        "total_requests": total_requests,
        "avg_latency_ms": round(float(avg_latency), 2),
        "total_errors": total_errors,
        "error_rate_percent": round(error_rate, 2),
    }


# Identifica os gargalos de performance (endpoints mais lentos) da aplicação
# Agrrupa por endpoint e método HTTP e calcula a latência média de cada um
def get_slowest_endpoints(
    db: Session, application_id: int, limit: int = 5
) -> List[dict]:
    results = (
        db.query(
            Metric.endpoint,
            Metric.method,
            func.avg(Metric.latency_ms).label("avg_latency"),
            func.count(Metric.id_metric).label("total_calls"),
        )
        .filter(Metric.application_id_application == application_id)
        .group_by(Metric.endpoint, Metric.method)
        .order_by(func.avg(Metric.latency_ms).desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "endpoint": res.endpoint,
            "method": res.method,
            "avg_latency_ms": round(float(res.avg_latency), 2),
            "total_calls": res.total_calls,
        }
        for res in results
    ]