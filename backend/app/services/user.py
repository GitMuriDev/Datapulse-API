from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password

# CRUD
# 1. CREATE (Criar)
def create_user(db: Session, user_in: UserCreate) -> User:
    hashed_pw = get_password_hash(user_in.password)
    db_user = User(
        user_name=user_in.user_name,
        email=user_in.email,
        password_hash=hashed_pw
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# 2. READ (Listar)
def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    return db.query(User).offset(skip).limit(limit).all()


# 3. UPDATE (Atualizar)
def update_user_by_id(db: Session, user_id: int, update_data: dict) -> Optional[User]:
    db_user = get_user_by_id(db, user_id=user_id)
    if not db_user:
        return None

    for field, value in update_data.items():
        if field == "password" and value:
            setattr(db_user, "passord_hash", get_password_hash(value))
        elif hasattr(db_user, field) and value is not None:
            setattr(db_user, field, value)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# 4. DELETE (Deletar)
def delete_user(db: Session, user_id: int) -> Optional[User]:
    db_user = get_user_by_id(db, user_id=user_id)
    if not db_user:
        return None

    db.delete(db_user)
    db.commit()
    return db_user

#FIMCRUD

# Buscar por ID
def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id_user == user_id).first()


# Buscar por email
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


# Autentica o usuário comparando o e-mail e o hash da senha para liberação do JWT.
def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


# Altera a senha do usuário exigindo a confirmação da senha atual por segurança.
def change_user_password(
    db: Session, user_id: int, current_password: str, new_password: str
) -> Optional[User]:
    db_user = get_user_by_id(db, user_id=user_id)
    if not db_user:
        return None
        
    if not verify_password(current_password, db_user.password_hash):
        return None
        
    db_user.password_hash = get_password_hash(new_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user