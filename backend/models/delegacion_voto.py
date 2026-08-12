from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from database import Base, utcnow
from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .vecino import Vecino


class DelegacionVoto(Base):
    __tablename__ = "delegaciones_voto"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    vecino_delegante_id: Mapped[int] = mapped_column(ForeignKey("vecinos.id"), nullable=False)
    vecino_delegado_id: Mapped[int] = mapped_column(ForeignKey("vecinos.id"), nullable=False)
    dni_delegante: Mapped[str | None] = mapped_column(String, nullable=True)
    asunto: Mapped[str | None] = mapped_column(String, nullable=True)
    fecha: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    fecha_validez: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    activa: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relaciones
    vecino_delegante: Mapped[Vecino] = relationship(
        "Vecino",
        foreign_keys=[vecino_delegante_id],
        back_populates="delegaciones_delegante",
    )
    vecino_delegado: Mapped[Vecino] = relationship(
        "Vecino",
        foreign_keys=[vecino_delegado_id],
        back_populates="delegaciones_delegado",
    )
