from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.core.security import SECRET_KEY, ALGORITHM
from app.models.user import User

# Indica ao FastAPI que as rotas protegidas esperam um token em /api/v1/auth/login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_db() -> Generator[Session, None, None]:
    # Garante a abertura e o fechamento correto da sessão com o PostgreSQL
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
        db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)       
) -> User:
    # Intercepta o Token JWT do cabeçalho Authorization: Bearer <token>,
    # valida a assinatura e injeta a entidade User correspondente na rota

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais de acesso",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except (jwt.PyJWTError, ValidationError):
        raise credentials_exception

    user = db.query(User).filter(User.id_user == int(user_id)).first()
    if not user:
        raise credentials_exception
        
    return user