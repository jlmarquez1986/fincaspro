from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from database import Base, utcnow
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .usuario import Usuario
    from .vecino import Vecino


class QuejaMejora(Base):
    __tablename__ = "quejas_mejoras"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tipo: Mapped[str] = mapped_column(String, nullable=False)
    categoria: Mapped[str] = mapped_column(String, nullable=False)
    asunto: Mapped[str] = mapped_column(String, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    estado: Mapped[str] = mapped_column(String, default="pendiente")
    prioridad: Mapped[str] = mapped_column(String, default="media")
    vecino_id: Mapped[int | None] = mapped_column(ForeignKey("vecinos.id"), nullable=True)
    creado_por: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    foto_path: Mapped[str | None] = mapped_column(String, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    actualizado: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)

    # Relaciones
    vecino: Mapped[Vecino | None] = relationship(
        "Vecino",
        back_populates="quejas_mejoras",
    )
    creado_por_usuario: Mapped[Usuario | None] = relationship(
        "Usuario",
        back_populates="quejas_mejoras_creadas",
    )
