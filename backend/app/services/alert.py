from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.alert import AlertRule, AlertLog, AlertStatus
from app.models.metric import Metric
from app.schemas.alert import AlertRuleCreate, AlertRuleUpdate

# CRUD de AlertRule
# 1. CREATE (Criar)
def create_alert_rule(db: Session, alertRule_in: AlertRuleCreate, application_id: int) -> AlertRule:
    db_alertRule = AlertRule(
        target=alertRule_in.target,
        condition=alertRule_in.condition,
        threshold=alertRule_in.threshold,
        window_min=alertRule_in.window_min,
        webhook_url=alertRule_in.webhook_url,
        application_id_application=application_id
    )
    db.add(db_alertRule)
    db.commit()
    db.refresh(db_alertRule)
    return db_alertRule


# 2. READ (Listar)
def get_alert_rules(db: Session, skip: int = 0, limit: int = 100) -> list[AlertRule]:
    return db.query(AlertRule).offset(skip).limit(limit).all()


# 3. UPDATE (Atualizar)
def update_alert_rule_by_id(db: Session, id_alert_rule: int, update_data: dict) -> Optional[AlertRule]:
    db_alertRule = get_alert_rule_by_id(db, id_alert_rule=id_alert_rule)
    if not db_alertRule:
        return None

    for field, value in update_data.items():
            # Protege o ID, a chave estrangeira e a data do evento de serem sobrescritos
            if field in ["id_alert_rule", "application_id_application"]:
                continue
            if hasattr(db_alertRule, field) and value is not None:
                setattr(db_alertRule, field, value)

    db.add(db_alertRule)
    db.commit()
    db.refresh(db_alertRule)
    return db_alertRule


# 4. DELETE (Deletar)
def delete_alert_rule(db: Session, id_alert_rule: int) -> Optional[AlertRule]:
    db_alertRule = get_alert_rule_by_id(db, id_alert_rule=id_alert_rule)
    if not db_alertRule:
        return None

    db.delete(db_alertRule)
    db.commit()
    return db_alertRule
    
#FIMCRUD

# Buscar por ID
def get_alert_rule_by_id(db: Session, id_alert_rule: int) -> Optional[AlertRule]:
    return db.query(AlertRule).filter(AlertRule.id_alert_rule == id_alert_rule).first()


# Lista apenas as regras de alerta pertencentes a uma aplicação específica.
def get_alert_rules_by_application(
    db: Session, application_id: int, skip: int = 0, limit: int = 100
) -> List[AlertRule]:
    return (
        db.query(AlertRule)
        .filter(AlertRule.application_id_application == application_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


# Motor de avaliação de alertas:
# 1. Busca todas as regras cadastradas para a aplicação.
# 2. Avalia as métricas dentro da janela de tempo (window_min).
# 3. Retorna a lista de regras violadas com a mensagem detalhada do incidente.
def evaluate_alert_rules_for_application(
    db: Session, application_id: int
) -> List[dict]:
    rules = get_alert_rules_by_application(db, application_id=application_id)
    triggered_events = []

    for rule in rules:
        time_window = datetime.utcnow() - timedelta(minutes=rule.window_min)
        
        # Avaliação para alvo de Latência Média (LATENCY)
        if rule.target.upper() == "LATENCY":
            avg_latency = (
                db.query(func.avg(Metric.latency_ms))
                .filter(
                    Metric.application_id_application == application_id,
                    Metric.timestamp >= time_window
                )
                .scalar() or 0.0
            )

            is_triggered = False
            if rule.condition == ">" and avg_latency > rule.threshold:
                is_triggered = True
            elif rule.condition == ">=" and avg_latency >= rule.threshold:
                is_triggered = True

            if is_triggered:
                triggered_events.append({
                    "rule": rule,
                    "message": f"Alerta de Latência: Média nos últimos {rule.window_min}min foi de {round(avg_latency, 2)}ms (Limite: {rule.threshold}ms)."
                })

        # Avaliação para alvo de Taxa/Quantidade de Erros (ERROR_RATE / ERRORS)
        elif rule.target.upper() in ["ERROR_RATE", "ERRORS"]:
            error_count = (
                db.query(func.count(Metric.id_metric))
                .filter(
                    Metric.application_id_application == application_id,
                    Metric.status_code >= 500,
                    Metric.timestamp >= time_window
                )
                .scalar() or 0
            )

            if error_count > rule.threshold:
                triggered_events.append({
                    "rule": rule,
                    "message": f"Alerta de Erros: Foram detectados {error_count} erros 5xx nos últimos {rule.window_min}min (Limite: {rule.threshold})."
                })

    return triggered_events


# Cria um novo registro de log quando um alerta é disparado
# Por padrão inicia como PENDING até ser entregue ao webhook
def create_alert_log(
    db: Session,
    alert_rule_id: int,
    message: str,
    status: AlertStatus = AlertStatus.PENDING,
) -> AlertLog:

    db_alert_log = AlertLog(
        message=message,
        status=status,
        alert_rules_id_alert_rule=alert_rule_id,
    )
    db.add(db_alert_log)
    db.commit()
    db.refresh(db_alert_log)
    return db_alert_log


# Lista todos os logs de alerta gerados no sistema (visão global)
def get_alert_logs(db: Session, skip: int = 0, limit: int = 100) -> List[AlertLog]:
    return db.query(AlertLog).offset(skip).limit(limit).all()


# Busca um log de alerta específico pelo ID primário
def get_alert_log_by_id(db: Session, id_alert_log: int) -> Optional[AlertLog]:
    return db.query(AlertLog).filter(AlertLog.id_alert_logs == id_alert_log).first()


# Lista o histórico auditável de disparos de alertas filtrado por aplicação
# Útil para exibir na aba de incidentes no Frontend
def get_alert_logs_by_application(
    db: Session, application_id: int, skip: int = 0, limit: int = 100
) -> List[AlertLog]:
    return (
        db.query(AlertLog)
        .join(AlertRule, AlertLog.alert_rules_id_alert_rule == AlertRule.id_alert_rules)
        .filter(AlertRule.application_id_application == application_id)
        .order_by(AlertLog.triggered_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

# Fluxo completo de observabilidade em produção:
 # 1. Executa o motor de avaliação de regras para a aplicação.
  # 2. Registra o AlertLog como PENDING no banco.
   # 3. Atualiza o status para SENT (ou FAILED) após simular/disparar o webhook.
def process_and_dispatch_alerts(db: Session, application_id: int) -> List[AlertLog]:
    triggered_events = evaluate_alert_rules_for_application(db, application_id=application_id)
    generated_logs = []

    for event in triggered_events:
        rule: AlertRule = event["rule"]
        message: str = event["message"]

        # Registra o incidente no banco
        log = create_alert_log(
            db=db,
            alert_rule_id=rule.id_alert_rules,
            message=message,
            status=AlertStatus.PENDING,
        )

        # Atualiza para SENT indicando que o evento foi processado
        log.status = AlertStatus.SENT
        db.add(log)
        db.commit()
        db.refresh(log)

        generated_logs.append(log)

    return generated_logs