from __future__ import annotations

from datetime import datetime

from database import Base, utcnow
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column


class Administrador(Base):
    __tablename__ = "administradores"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    entidad: Mapped[str] = mapped_column(String, nullable=False)
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    telefono: Mapped[str | None] = mapped_column(String, nullable=True)
    email: Mapped[str | None] = mapped_column(String, nullable=True)
    direccion: Mapped[str | None] = mapped_column(String, nullable=True)
    observaciones: Mapped[str | None] = mapped_column(String, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    actualizado: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)
