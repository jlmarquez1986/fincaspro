from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from database import Base, utcnow
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .vecino import Vecino


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    asunto: Mapped[str] = mapped_column(String, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    categoria: Mapped[str] = mapped_column(String, default="otros")
    prioridad: Mapped[str] = mapped_column(String, default="normal")
    estado: Mapped[str] = mapped_column(String, default="pendiente")
    piso: Mapped[str | None] = mapped_column(String, nullable=True)
    vecino_id: Mapped[int | None] = mapped_column(ForeignKey("vecinos.id"), nullable=True)
    asignado_a: Mapped[str | None] = mapped_column(String, nullable=True)
    foto_path: Mapped[str | None] = mapped_column(String, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    actualizado: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)
    alcance: Mapped[str | None] = mapped_column(String, nullable=True)

    # Relaciones
    vecino: Mapped[Vecino | None] = relationship(
        "Vecino",
        back_populates="tickets",
    )
    comentarios: Mapped[list[Comentario]] = relationship(
        "Comentario",
        back_populates="ticket",
        cascade="all, delete-orphan",
    )


class Comentario(Base):
    __tablename__ = "comentarios"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"), nullable=False)
    autor: Mapped[str] = mapped_column(String, default="Conserje")
    texto: Mapped[str] = mapped_column(Text, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    # Relaciones
    ticket: Mapped[Ticket] = relationship(
        "Ticket",
        back_populates="comentarios",
    )
