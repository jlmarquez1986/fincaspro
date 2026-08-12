from __future__ import annotations

from datetime import datetime

from database import Base, utcnow
from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class EstadoCuenta(Base):
    __tablename__ = "estados_cuenta"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    entidad: Mapped[str] = mapped_column(String, nullable=False)
    mes: Mapped[int] = mapped_column(Integer, nullable=False)
    anio: Mapped[int] = mapped_column(Integer, nullable=False)
    saldo_inicial: Mapped[float] = mapped_column(Float, default=0.0)
    ingresos: Mapped[float] = mapped_column(Float, default=0.0)
    gastos: Mapped[float] = mapped_column(Float, default=0.0)
    saldo_final: Mapped[float] = mapped_column(Float, default=0.0)
    observaciones: Mapped[str | None] = mapped_column(String, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    actualizado: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)
