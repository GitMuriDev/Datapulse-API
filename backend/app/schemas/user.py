from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

# Schema Base (campos compartilhados). BaseModel garante uma validação segura dos dados
class UserBase(BaseModel):
    user_name: str
    # EmailStr valida se o que foi escrito realmente é um email
    email: EmailStr

# Schema para criação de usuário (entrada no POST /user). Herda o UserBase para usar os atributos da classe para a criação de usuário
class UserCreate(UserBase):
    password: str

# Schema para resposta pública (saída no GET /user) - Oculta a senha
class UserResponse(UserBase):
    id_user: int
    created_at: datetime

    # É uma forma do banco de dados se conectar e entender o Pydantic
    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserPasswordChange(BaseModel):
    current_password: str
    new_password: str