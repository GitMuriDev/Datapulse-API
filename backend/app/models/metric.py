from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base

# Classe metric e seus atributos individuais
class Metric(Base):
    __tablename__ = "metric"

    id_metric: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    endpoint: Mapped[str] = mapped_column(String(255), nullable=False)
    method: Mapped[str] = mapped_column(String(45), nullable=False)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relacionamento com application
    application_id_application: Mapped[int] = mapped_column(
        Integer, ForeignKey("application.id_application", ondelete="CASCADE"), nullable=False
    )

    application: Mapped["Application"] = relationship("Application", back_populates="metrics")