from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any

# Criação de metrica com regras que garantem uma criação lógica possível
class MetricCreate(BaseModel):
    endpoint: str
    method: str
    status_code: int = Field(..., ge=100, le=599) # Exige que o status esteja entre 100 e 599
    latency_ms: float = Field(..., ge=0) # Exige que a latência seja maior ou igual a 0

class MetricResponse(MetricCreate):
    id_metrics: int
    timestamp: datetime
    application_id_application: int

    # É uma forma do banco de dados se conectar e entender o Pydantic
    model_config = ConfigDict(from_attributes=True)


class MetricUpdate(BaseModel):
    endpoint: Optional[str] = None
    method: Optional[str] = None
    status_code: Optional[int] = None
    response_time_ms: Optional[float] = None
    metadata_info: Optional[Dict[str, Any]] = None


class ApplicationPerformanceSummary(BaseModel):
    application_id: int
    total_requests: int
    avg_response_time_ms: float
    error_rate: float
    status_distribution: Dict[str, int]


class SlowestEndpointSummary(BaseModel):
    endpoint: str
    method: str
    avg_response_time_ms: float
    request_count: int