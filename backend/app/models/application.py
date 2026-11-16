from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base

# Classe application e seus atributos individuais
class Application(Base):
    __tablename__ = "application"

    id_application: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    application_name: Mapped[str] = mapped_column(String(100), nullable=False)
    api_key: Mapped[str] = mapped_column(String(65), unique=True, nullable=False, index=True)
    api_secret_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Chave Estrangeira apontando para a tabela user (id_user)
    user_id_user: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id_user", ondelete="CASCADE"), nullable=False
    )

    # Relacionamentos com metrics e alert_rules
    owner: Mapped["User"] = relationship("User", back_populates="applications")

    metrics: Mapped[list["Metric"]] = relationship(
        "Metric", back_populates="application", cascade="all, delete-orphan"
    )

    alert_rules: Mapped[list["AlertRule"]] = relationship(
        "AlertRule", back_populates="application", cascade="all, delete-orphan"
    )