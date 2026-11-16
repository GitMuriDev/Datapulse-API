from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models.application import Application
from app.models.user import User
from app.schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationResponse,
    ApplicationWithSecretResponse,
)
from app.services import application as application_service

router = APIRouter()

# CRUD
# 1. CREATE (Criar)
@router.post(
    "/",
    response_model=ApplicationWithSecretResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar nova aplicação",
    description="Cria uma nova aplicação vinculada ao usuário logado e retorna a API Key e o API Secret (exibido apenas uma vez).",
)
def create_application(
    *,
    db: Session = Depends(deps.get_db),
    application_in: ApplicationCreate,
    current_user: User = Depends(deps.get_current_user),
) -> dict:
    app, api_secret = application_service.create_application(
        db=db, application_in=application_in, user_id=current_user.id_user
    )
    
    # Retorna o modelo ORM acrescido do api_secret em texto puro
    return {
        "id_application": app.id_application,
        "application_name": app.application_name,
        "api_key": app.api_key,
        "user_id_user": app.user_id_user,
        "api_secret": api_secret,
    }


# 2. READ (Listar)
@router.get(
    "/",
    response_model=List[ApplicationResponse],
    summary="Listar todas as aplicações (Admin)",
    description="Retorna a lista paginada de todas as aplicações cadastradas no sistema.",
)
def get_applications(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> List[Application]:
    return application_service.get_applications(db, skip=skip, limit=limit)


# 3. UPDATE (Atualizar)
@router.put(
    "/{application_id}",
    response_model=ApplicationResponse,
    summary="Atualizar dados da aplicação",
    description="Atualiza informações cadastrais da aplicação. Apenas o proprietário pode realizar a alteração.",
)
def update_application_by_id(
    *,
    db: Session = Depends(deps.get_db),
    application_id: int,
    application_in: ApplicationUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Application:
    app = application_service.get_application_by_id(db, application_id=application_id)
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aplicação não encontrada.",
        )
    
    # Impede que um usuário altere aplicações de terceiros
    if app.user_id_user != current_user.id_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para alterar esta aplicação.",
        )

    update_data = application_in.model_dump(exclude_unset=True)
    return application_service.update_application_by_id(
        db, application_id=application_id, update_data=update_data
    )


# 4. DELETE (Deletar)
@router.delete(
    "/{application_id}",
    response_model=ApplicationResponse,
    summary="Deletar aplicação",
    description="Remove uma aplicação do sistema. Apenas o proprietário pode deletar.",
)
def delete_application(
    *,
    db: Session = Depends(deps.get_db),
    application_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Application:
    app = application_service.get_application_by_id(db, application_id=application_id)
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aplicação não encontrada.",
        )
    
    if app.user_id_user != current_user.id_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para deletar esta aplicação.",
        )

    return application_service.delete_application(db, application_id=application_id)

# FIMCRUD

# Buscar por ID
@router.get(
    "/{application_id}",
    response_model=ApplicationResponse,
    summary="Buscar aplicação por ID",
    description="Retorna os detalhes de uma aplicação específica.",
)
def get_application_by_id(
    application_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Application:
    app = application_service.get_application_by_id(db, application_id=application_id)
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aplicação não encontrada.",
        )
    
    if app.user_id_user != current_user.id_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para acessar esta aplicação.",
        )
    return app


# Busca apenas as aplicações pertencentes ao usuário autenticado (Multi-tenancy).
@router.get(
    "/me/my-applications",
    response_model=List[ApplicationResponse],
    summary="Listar minhas aplicações",
    description="Retorna as aplicações pertencentes ao usuário atualmente autenticado.",
)
def get_applications_by_user(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> List[Application]:
    return application_service.get_applications_by_user(
        db, user_id=current_user.id_user, skip=skip, limit=limit
    )


# Buscar por API Key
@router.get(
    "/by-key/{api_key}",
    response_model=ApplicationResponse,
    summary="Buscar aplicação por API Key",
    description="Busca uma aplicação utilizando a API Key cadastrada.",
)
def get_application_by_key(
    api_key: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Application:
    app = application_service.get_application_by_key(db, api_key=api_key)
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aplicação não encontrada com a API Key informada.",
        )
    
    if app.user_id_user != current_user.id_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para acessar esta aplicação.",
        )
    return app


# Valida a combinação de API Key e API Secret
@router.post(
    "/authenticate",
    response_model=ApplicationResponse,
    summary="Autenticar aplicação por credenciais",
    description="Valida se a combinação de API Key e API Secret é válida.",
)
def authenticate_application(
    *,
    db: Session = Depends(deps.get_db),
    api_key: str,
    api_secret: str,
) -> Application:
    app = application_service.authenticate_application(
        db, api_key=api_key, api_secret=api_secret
    )
    if not app:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais de aplicação inválidas.",
        )
    return app


# Rotacionar API Secret de uma aplicação
@router.post(
    "/{application_id}/rotate-secret",
    response_model=ApplicationWithSecretResponse,
    summary="Rotacionar API Secret",
    description="Regenera o API Secret de uma aplicação em caso de vazamento.",
)
def rotate_application_secret(
    *,
    db: Session = Depends(deps.get_db),
    application_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> dict:
    result = application_service.rotate_application_secret(
        db, application_id=application_id, user_id=current_user.id_user
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aplicação não encontrada ou permissão negada.",
        )
    
    app, new_api_secret = result
    return {
        "id_application": app.id_application,
        "application_name": app.application_name,
        "api_key": app.api_key,
        "user_id_user": app.user_id_user,
        "api_secret": new_api_secret,
    }