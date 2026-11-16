from datetime import datetime
from sqlalchemy import String, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base


# Classe usuário e seus atributos individuais
class User(Base):
    __tablename__ = "user"

    id_user: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_name: Mapped[str] = mapped_column(String(45), nullable=False)
    email: Mapped[str] = mapped_column(String(45), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relacionamento 1 : N com a tabela Application 
    applications: Mapped[list["Application"]] = relationship(
        "Application", back_populates="owner", cascade="all, delete-orphan"
    )

