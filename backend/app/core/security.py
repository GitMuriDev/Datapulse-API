from datetime import datetime, timedelta, timezone
from typing import Any
import secrets
from passlib.context import CryptContext
import jwt
import os
from dotenv import load_dotenv

# Define o algoritmo de hash padrão (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))

if not SECRET_KEY:
    raise ValueError("A variável de ambiente SECRET_KEY não foi definida no arquivo .env")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Verifica se a senha fornecida bate com o hash salvo
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    # Gera o hash Bcrypt da senha do usuário
    return pwd_context.hash(password)


def create_access_token(subject: str | Any, expires_delta: timedelta | None = None) -> str:
    # Gera um Token JWT assinado contendo a identidade do usuário (user_id)
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def generate_api_credentials() -> tuple[str, str, str]:
    #Gera as credenciais de uma nova aplicação monitorada:
    #- api_key: Chave pública com prefixo (ex: dp_live_abc123...)
    #- api_secret: Segredo em texto puro (exibido apenas UMA vez ao usuário)
    #- api_secret_hash: Hash Bcrypt do segredo (armazenado no banco)

    api_key = f"dp_live_{secrets.token_hex(16)}"
    api_secret = f"sec_{secrets.token_hex(32)}"
    api_secret_hash = pwd_context.hash(api_secret)
    
    return api_key, api_secret, api_secret_hash