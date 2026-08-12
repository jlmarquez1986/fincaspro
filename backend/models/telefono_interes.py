from __future__ import annotations

from datetime import datetime

from database import Base, utcnow
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column


class TelefonoInteres(Base):
    __tablename__ = "telefonos_interes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    telefono: Mapped[str] = mapped_column(String, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String, nullable=True)
    categoria: Mapped[str | None] = mapped_column(String, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    actualizado: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)
