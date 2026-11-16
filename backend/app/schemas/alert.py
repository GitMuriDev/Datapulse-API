from datetime import datetime
from pydantic import BaseModel, HttpUrl, ConfigDict
from app.models.alert import AlertStatus
from typing import Optional

class AlertRuleBase(BaseModel):
    target: str
    condition: str
    threshold: float
    window_min: int
    webhook_url: str

# Criação de AlertRule pegando apenas o que ja foi definido na base
class AlertRuleCreate(AlertRuleBase):
    pass

# O que aparece no response
class AlertRuleResponse(AlertRuleBase):
    id_alert_rule: int
    application_id_application: int

    model_config = ConfigDict(from_attributes=True)

# O que aparece no response do AlertLogs
class AlertLogResponse(BaseModel):
    id_alert_logs: int
    message: str
    status: AlertStatus
    triggered_at: datetime
    alert_rule_id_alert_rule: int

    model_config = ConfigDict(from_attributes=True)



class AlertRuleUpdate(BaseModel):
    name: Optional[str] = None
    metric_type: Optional[str] = None
    condition: Optional[str] = None
    threshold: Optional[float] = None
    is_active: Optional[bool] = None