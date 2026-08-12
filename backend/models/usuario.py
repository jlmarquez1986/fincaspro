from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from database import Base, utcnow
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .queja_mejora import QuejaMejora
    from .registro_piscina import RegistroPiscina


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    rol: Mapped[str] = mapped_column(String, default="conserje")
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    # Relaciones
    quejas_mejoras_creadas: Mapped[list[QuejaMejora]] = relationship(
        "QuejaMejora",
        back_populates="creado_por_usuario",
    )
    registros_piscina_creados: Mapped[list[RegistroPiscina]] = relationship(
        "RegistroPiscina",
        back_populates="registrado_por_usuario",
    )
