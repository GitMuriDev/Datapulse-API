from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserPasswordChange
from app.services import user as user_service

router = APIRouter()

# CRUD
# 1. CREATE (Criar)
@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar novo usuário",
    description="Registra um novo usuário no sistema. Valida se o e-mail já está cadastrado.",
)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
) -> User:
    user = user_service.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O e-mail informado já está cadastrado no sistema.",
        )
    return user_service.create_user(db=db, user_in=user_in)


# 2. READ (Listar)
@router.get(
    "/",
    response_model=List[UserResponse],
    summary="Listar usuários",
    description="Retorna a lista paginada de usuários cadastrados no sistema.",
)
def get_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> List[User]:
    return user_service.get_users(db, skip=skip, limit=limit)


# 3. UPDATE (Atualizar)
@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Atualizar dados do usuário",
    description="Atualiza informações cadastrais do usuário. Usuários só podem atualizar seu próprio perfil.",
)
def update_user_by_id(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> User:
    # Impede que um usuário edite o perfil de outro
    if current_user.id_user != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para alterar os dados de outro usuário.",
        )

    user = user_service.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )

    update_data = user_in.model_dump(exclude_unset=True)
    return user_service.update_user_by_id(db, user_id=user_id, update_data=update_data)


# 4. DELETE (Deletar)
@router.delete(
    "/{user_id}",
    response_model=UserResponse,
    summary="Deletar usuário",
    description="Remove a conta do usuário. Usuários só podem remover a própria conta.",
)
def delete_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> User:
    if current_user.id_user != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para remover a conta de outro usuário.",
        )

    deleted_user = user_service.delete_user(db, user_id=user_id)
    if not deleted_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )
    return deleted_user

# FIMCRUD

# Buscar por ID
@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Buscar usuário por ID",
    description="Retorna os detalhes de um usuário específico pelo seu ID primário.",
)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> User:
    user = user_service.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )
    return user


# Obter perfil do usuário logado (Busca por e-mail/token)
@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obter perfil do usuário logado",
    description="Retorna os dados cadastrais do usuário atualmente autenticado via Token JWT.",
)
def get_user_me(
    current_user: User = Depends(deps.get_current_user),
) -> User:
    return current_user


# Altera a senha do usuário exigindo a confirmação da senha atual por segurança.
@router.patch(
    "/me/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Alterar senha do usuário logado",
    description="Exige a validação da senha atual antes de definir a nova senha hashed.",
)
def change_user_password(
    *,
    db: Session = Depends(deps.get_db),
    password_in: UserPasswordChange,
    current_user: User = Depends(deps.get_current_user),
) -> None:
    updated_user = user_service.change_user_password(
        db=db,
        user_id=current_user.id_user,
        current_password=password_in.current_password,
        new_password=password_in.new_password,
    )
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A senha atual informada está incorreta.",
        )