from __future__ import annotations

from datetime import datetime

from database import Base, utcnow
from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column


class Aviso(Base):
    __tablename__ = "avisos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    titulo: Mapped[str] = mapped_column(String, nullable=False)
    contenido: Mapped[str] = mapped_column(Text, nullable=False)
    tipo: Mapped[str] = mapped_column(String, default="info")
    activo: Mapped[str] = mapped_column(String, default="true")
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
