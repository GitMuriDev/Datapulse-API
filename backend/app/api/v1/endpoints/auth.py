from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api import deps
from app.core import security
from app.schemas.token import Token
from app.services import user as user_service

router = APIRouter()


@router.post(
    "/login/access-token",
    response_model=Token,
    summary="Autenticar usuário e gerar Token JWT",
    description="Recebe e-mail (no campo username) e senha via Form Data padrão OAuth2 e retorna o token de acesso Bearer.",
) # Endpoint OAuth2 compatível com a documentação automática do Swagger (/docs).
def login_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    user = user_service.authenticate_user(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Define o tempo de expiração do token (ex: 60 minutos)
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    return {
        "access_token": security.create_access_token(
            user.id_user, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }