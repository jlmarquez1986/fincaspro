from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from database import Base, utcnow
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .vecino import Vecino


class Paquete(Base):
    __tablename__ = "paquetes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    remitente: Mapped[str | None] = mapped_column(String, nullable=True)
    vecino_id: Mapped[int] = mapped_column(ForeignKey("vecinos.id"), nullable=False)
    tracking: Mapped[str | None] = mapped_column(String, nullable=True)
    tamanio: Mapped[str] = mapped_column(String, default="mediano")
    estado: Mapped[str] = mapped_column(String, default="pendiente")
    notificado: Mapped[str] = mapped_column(String, default="no")
    recibido_en: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    entregado_en: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relaciones
    vecino: Mapped[Vecino] = relationship(
        "Vecino",
        back_populates="paquetes",
    )
