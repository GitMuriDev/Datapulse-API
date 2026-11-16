import enum
from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Enum, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base


# Classe Enum, para definir status
class AlertStatus(str, enum.Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"


# Classe AlertRule e seus atributos individuais
class AlertRule(Base):
    __tablename__ = "alert_rule"

    id_alert_rule: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    target: Mapped[str] = mapped_column(String(45), nullable=False)
    condition: Mapped[str] = mapped_column(String(45), nullable=False)
    threshold: Mapped[float] = mapped_column(Float, nullable=False)
    window_min: Mapped[int] = mapped_column(Integer, nullable=False)
    webhook_url: Mapped[str] = mapped_column(String(145), nullable=False)

    # Relação com application
    application_id_application: Mapped[int] = mapped_column(
        Integer, ForeignKey("application.id_application", ondelete="CASCADE"), nullable=False
    )

    application: Mapped["Application"] = relationship("Application", back_populates="alert_rules")
    logs: Mapped[list["AlertLog"]] = relationship(
        "AlertLog", back_populates="alert_rule", cascade="all, delete-orphan"
    )

# Classe AlertLogs e seus atributos individuais
class AlertLog(Base):
    __tablename__ = "alert_log"

    id_alert_logs: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    # Sua relação com a classe Enum
    status: Mapped[AlertStatus] = mapped_column(
        Enum(AlertStatus), default=AlertStatus.PENDING, nullable=False
    )
    
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Sua relação com a classe alertrule
    alert_rules_id_alert_rule: Mapped[int] = mapped_column(
        Integer, ForeignKey("alert_rule.id_alert_rule", ondelete="CASCADE")
    )

    alert_rule: Mapped["AlertRule"] = relationship("AlertRule", back_populates="logs")
