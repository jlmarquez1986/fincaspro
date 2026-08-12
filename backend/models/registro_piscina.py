from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from database import Base, utcnow
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .usuario import Usuario
    from .vecino import Vecino


class RegistroPiscina(Base):
    __tablename__ = "registros_piscina"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    vecino_id: Mapped[int] = mapped_column(ForeignKey("vecinos.id"), nullable=False)
    tipo: Mapped[str] = mapped_column(String, nullable=False)
    nombre_invitado: Mapped[str | None] = mapped_column(String, nullable=True)
    fecha_hora: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    registrado_por: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)

    # Relaciones
    vecino: Mapped[Vecino] = relationship(
        "Vecino",
        back_populates="registros_piscina",
    )
    registrado_por_usuario: Mapped[Usuario] = relationship(
        "Usuario",
        back_populates="registros_piscina_creados",
    )
