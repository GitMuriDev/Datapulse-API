from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models.alert import AlertRule, AlertLog
from app.models.user import User
from app.schemas.alert import (
    AlertRuleCreate,
    AlertRuleUpdate,
    AlertRuleResponse,
    AlertLogResponse,
)
from app.services import alert as alert_service
from app.services import application as application_service

router = APIRouter()

# CRUD de AlertRule
# 1. CREATE (Criar)
@router.post(
    "/rules/application/{application_id}",
    response_model=AlertRuleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar nova regra de alerta",
    description="Cria uma nova regra de monitoramento (latência ou erros) para uma aplicação específica.",
)
def create_alert_rule(
    *,
    db: Session = Depends(deps.get_db),
    application_id: int,
    alert_rule_in: AlertRuleCreate,
    current_user: User = Depends(deps.get_current_user),
) -> AlertRule:
    app = application_service.get_application_by_id(db, application_id=application_id)
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aplicação não encontrada.",
        )
    if app.user_id_user != current_user.id_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para criar regras para esta aplicação.",
        )

    return alert_service.create_alert_rule(
        db=db, alertRule_in=alert_rule_in, application_id=application_id
    )


# 2. READ (Listar)
@router.get(
    "/rules",
    response_model=List[AlertRuleResponse],
    summary="Listar todas as regras de alerta (Admin)",
    description="Retorna a lista paginada de todas as regras de alerta cadastradas no sistema.",
)
def get_alert_rules(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> List[AlertRule]:
    return alert_service.get_alert_rules(db, skip=skip, limit=limit)


# 3. UPDATE (Atualizar)
@router.put(
    "/rules/{id_alert_rule}",
    response_model=AlertRuleResponse,
    summary="Atualizar regra de alerta por ID",
    description="Atualiza as configurações de limite, janela de tempo ou webhook de uma regra.",
)
def update_alert_rule_by_id(
    *,
    db: Session = Depends(deps.get_db),
    id_alert_rule: int,
    alert_rule_in: AlertRuleUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> AlertRule:
    rule = alert_service.get_alert_rule_by_id(db, id_alert_rule=id_alert_rule)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regra de alerta não encontrada.",
        )

    app = application_service.get_application_by_id(
        db, application_id=rule.application_id_application
    )
    if not app or app.user_id_user != current_user.id_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para alterar esta regra de alerta.",
        )

    update_data = alert_rule_in.model_dump(exclude_unset=True)
    return alert_service.update_alert_rule_by_id(
        db, id_alert_rule=id_alert_rule, update_data=update_data
    )


# 4. DELETE (Deletar)
@router.delete(
    "/rules/{id_alert_rule}",
    response_model=AlertRuleResponse,
    summary="Deletar regra de alerta por ID",
    description="Remove uma regra de alerta do sistema.",
)
def delete_alert_rule(
    *,
    db: Session = Depends(deps.get_db),
    id_alert_rule: int,
    current_user: User = Depends(deps.get_current_user),
) -> AlertRule:
    rule = alert_service.get_alert_rule_by_id(db, id_alert_rule=id_alert_rule)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regra de alerta não encontrada.",
        )

    app = application_service.get_application_by_id(
        db, application_id=rule.application_id_application
    )
    if not app or app.user_id_user != current_user.id_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para remover esta regra de alerta.",
        )

    return alert_service.delete_alert_rule(db, id_alert_rule=id_alert_rule)

# FIMCRUD

# Buscar por ID
@router.get(
    "/rules/{id_alert_rule}",
    response_model=AlertRuleResponse,
    summary="Buscar regra de alerta por ID",
    description="Retorna os detalhes de uma regra de alerta específica.",
)
def get_alert_rule_by_id(
    id_alert_rule: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> AlertRule:
    rule = alert_service.get_alert_rule_by_id(db, id_alert_rule=id_alert_rule)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regra de alerta não encontrada.",
        )

    app = application_service.get_application_by_id(
        db, application_id=rule.application_id_application
    )
    if not app or app.user_id_user != current_user.id_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para acessar esta regra.",
        )
    return rule


# Lista apenas as regras de alerta pertencentes a uma aplicação específica
@router.get(
    "/rules/application/{application_id}",
    response_model=List[AlertRuleResponse],
    summary="Listar regras por aplicação",
    description="Retorna todas as regras de monitoramento ativas de uma aplicação.",
)
def get_alert_rules_by_application(
    application_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> List[AlertRule]:
    app = application_service.get_application_by_id(db, application_id=application_id)
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aplicação não encontrada.",
        )
    if app.user_id_user != current_user.id_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para visualizar estas regras.",
        )

    return alert_service.get_alert_rules_by_application(
        db, application_id=application_id, skip=skip, limit=limit
    )


# Motor de avaliação de alertas (Dry-run / Avaliação)
@router.get(
    "/evaluate/application/{application_id}",
    summary="Avaliar regras da aplicação",
    description="Executa o motor de testes sobre as métricas recentes e retorna eventuais violações sem disparar webhooks.",
)
def evaluate_alert_rules_for_application(
    application_id: int,
    db: Session = Depends(deps.get_db),
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
            detail="Você não tem permissão para avaliar alertas desta aplicação.",
        )

    return alert_service.evaluate_alert_rules_for_application(
        db, application_id=application_id
    )


# Criar log de alerta manualmente (Interno/Testes)
@router.post(
    "/logs/rule/{id_alert_rule}",
    response_model=AlertLogResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar log de alerta",
    description="Regista manualmente um log de disparo associado a uma regra de alerta.",
)
def create_alert_log(
    *,
    db: Session = Depends(deps.get_db),
    id_alert_rule: int,
    message: str,
    current_user: User = Depends(deps.get_current_user),
) -> AlertLog:
    rule = alert_service.get_alert_rule_by_id(db, id_alert_rule=id_alert_rule)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regra de alerta não encontrada.",
        )

    app = application_service.get_application_by_id(
        db, application_id=rule.application_id_application
    )
    if not app or app.user_id_user != current_user.id_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para registar logs nesta regra.",
        )

    return alert_service.create_alert_log(
        db=db, alert_rule_id=id_alert_rule, message=message
    )


# Lista todos os logs de alerta gerados no sistema (visão global)
@router.get(
    "/logs",
    response_model=List[AlertLogResponse],
    summary="Listar todos os logs de alerta (Admin)",
    description="Retorna a lista de auditoria global de alertas disparados no sistema.",
)
def get_alert_logs(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> List[AlertLog]:
    return alert_service.get_alert_logs(db, skip=skip, limit=limit)


# Busca um log de alerta específico pelo ID primário
@router.get(
    "/logs/{id_alert_log}",
    response_model=AlertLogResponse,
    summary="Buscar log de alerta por ID",
    description="Retorna os detalhes de um evento de disparo específico.",
)
def get_alert_log_by_id(
    id_alert_log: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> AlertLog:
    log = alert_service.get_alert_log_by_id(db, id_alert_log=id_alert_log)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log de alerta não encontrado.",
        )
    return log


# Lista o histórico auditável de disparos de alertas filtrado por aplicação
@router.get(
    "/logs/application/{application_id}",
    response_model=List[AlertLogResponse],
    summary="Listar histórico de incidentes por aplicação",
    description="Retorna os logs de disparos de alerta de uma determinada aplicação para exibição no Dashboard.",
)
def get_alert_logs_by_application(
    application_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> List[AlertLog]:
    app = application_service.get_application_by_id(db, application_id=application_id)
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aplicação não encontrada.",
        )
    if app.user_id_user != current_user.id_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para visualizar os incidentes desta aplicação.",
        )

    return alert_service.get_alert_logs_by_application(
        db, application_id=application_id, skip=skip, limit=limit
    )


# Processamento e disparo completo de alertas
@router.post(
    "/dispatch/application/{application_id}",
    response_model=List[AlertLogResponse],
    summary="Processar e disparar alertas da aplicação",
    description="Avalia as regras ativas, cria registros de incidentes e dispara as notificações configuradas.",
)
def process_and_dispatch_alerts(
    application_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> List[AlertLog]:
    app = application_service.get_application_by_id(db, application_id=application_id)
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aplicação não encontrada.",
        )
    if app.user_id_user != current_user.id_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para disparar alertas desta aplicação.",
        )

    return alert_service.process_and_dispatch_alerts(db, application_id=application_id)