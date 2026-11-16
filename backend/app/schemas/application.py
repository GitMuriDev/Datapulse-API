from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

# Schema Base (campos compartilhados). BaseModel garante uma validação segura dos dados
class ApplicationBase(BaseModel):
    application_name: str

# A aplicação só precisa do nome para ser criada, ja que o software se encarrega de todo o resto
class ApplicationCreate(ApplicationBase):
    pass

# Resposta da API ao criar uma aplicação (retonar a chave API em texto puro uma única vez)
class ApplicationCreateResponse(ApplicationBase):
    id_application: int
    api_key: str
    api_secret: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Retorna as informações padrões da aplicação, oculatando a senha
class ApplicationResponse(ApplicationBase):
    id_application: int
    api_key: str
    created_at: datetime

    # É uma forma do banco de dados se conectar e entender o Pydantic
    model_config = ConfigDict(from_attributes=True)



class ApplicationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ApplicationWithSecretResponse(ApplicationResponse):
    api_key: str