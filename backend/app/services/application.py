from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.application import Application
from app.schemas.application import ApplicationCreate
from app.core.security import generate_api_credentials
from app.core.security import verify_password

# CRUD
# 1. CREATE (Criar)
def create_application(
    db: Session, application_in: ApplicationCreate, user_id: int
) -> tuple[Application, str]:
    # Gera as credenciais (api_key, api_secret, api_secret_hash)
    api_key, api_secret, api_secret_hash = generate_api_credentials()

    # Instancia a aplicação sem encostar em ID primário (deixa o postgresql gerar)
    db_application = Application(
        application_name=application_in.application_name,
        api_key=api_key,
        api_secret_hash=api_secret_hash,
        user_id_user=user_id,  # Chave estrangeira indicando o dono da aplicação
    )

    db.add(db_application)
    db.commit()
    db.refresh(db_application)  
    return db_application, api_secret


# 2. READ (Listar)
def get_applications(db: Session, skip: int = 0, limit: int = 100) -> list[Application]:
    return db.query(Application).offset(skip).limit(limit).all()


# 3. UPDATE (Atualizar)
def update_application_by_id(
    db: Session, application_id: int, update_data: dict
) -> Optional[Application]:
    db_application = get_application_by_id(db, application_id=application_id)
    if not db_application:
        return None

    for field, value in update_data.items():
        # Impede a alteração acidental de chaves e relacionamentos via update simples
        if field in ["api_key", "api_secret_hash", "id_application", "user_id_user"]:
            continue
        if hasattr(db_application, field) and value is not None:
            setattr(db_application, field, value)

    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application


# 4. DELET (Deletar)
def delete_application(db: Session, application_id: int) -> Optional[Application]:
    db_application = get_application_by_id(db, application_id=application_id)
    if not db_application:
        return None

    db.delete(db_application)
    db.commit()
    return db_application

#FIMCRUD

# Buscar por ID 
def get_application_by_id(db: Session, application_id: int) -> Optional[Application]:
    return db.query(Application).filter(Application.id_application == application_id).first()


# Busca apenas as aplicações pertencentes ao usuário autenticado.
# Essencial para garantir isolamento de dados (Multi-tenancy).
def get_applications_by_user(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> list[Application]:
    return (
        db.query(Application)
        .filter(Application.user_id_user == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


# Usado pelo middleware de Ingestão de Métricas para validar 
# se a requisição vinda de um SDK/sistema externo possui uma API Key válida.
def get_application_by_key(db: Session, api_key: str) -> Optional[Application]:
    
    return db.query(Application).filter(Application.api_key == api_key).first()


# Valida a combinação de API Key e API Secret em chamadas que exigem 
# autenticação estrita da aplicação consumidora (ex: alteração de configurações via agent).
def authenticate_application(
    db: Session, api_key: str, api_secret: str
) -> Optional[Application]:
    app = get_application_by_key(db, api_key=api_key)
    if not app:
        return None
    if not verify_password(api_secret, app.api_secret_hash):
        return None
    return app


# Recurso crítico de segurança em nuvem:
# Caso o secret de uma aplicação vaze, o usuário pode rotacionar (regenerar) 
# o segredo sem precisar excluir e recriar toda a aplicação.
def rotate_application_secret(
    db: Session, application_id: int, user_id: int
) -> Optional[tuple[Application, str]]:

    db_application = get_application_by_id(db, application_id=application_id)
    
    # Garante que a aplicação existe e pertence ao usuário solicitante
    if not db_application or db_application.user_id_user != user_id:
        return None

    _, new_api_secret, new_api_secret_hash = generate_api_credentials()
    db_application.api_secret_hash = new_api_secret_hash

    db.add(db_application)
    db.commit()
    db.refresh(db_application)

    return db_application, new_api_secret