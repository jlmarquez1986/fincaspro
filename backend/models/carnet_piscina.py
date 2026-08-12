from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from database import Base, utcnow
from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .vecino import Vecino


class CarnetPiscina(Base):
    __tablename__ = "carnets_piscina"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    vecino_id: Mapped[int] = mapped_column(ForeignKey("vecinos.id"), unique=True, nullable=False)
    numero_carnet: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    fecha_expedicion: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relación 1:1
    vecino: Mapped[Vecino] = relationship(
        "Vecino",
        back_populates="carnet_piscina",
    )
