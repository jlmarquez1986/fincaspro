from __future__ import annotations

from database import Base
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class Configuracion(Base):
    __tablename__ = "configuraciones"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    clave: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    valor: Mapped[str] = mapped_column(String, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String, nullable=True)
