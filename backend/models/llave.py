from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from database import Base
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .vecino import Vecino


class Llave(Base):
    __tablename__ = "llaves"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    codigo: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String, nullable=True)
    estado: Mapped[str] = mapped_column(String, default="disponible")
    prestada_a: Mapped[str | None] = mapped_column(String, nullable=True)
    vecino_id: Mapped[int | None] = mapped_column(ForeignKey("vecinos.id"), nullable=True)
    desde: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relaciones
    vecino: Mapped[Vecino | None] = relationship(
        "Vecino",
        back_populates="llaves",
    )
