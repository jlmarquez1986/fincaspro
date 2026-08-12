from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from database import Base, utcnow
from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .carnet_piscina import CarnetPiscina
    from .delegacion_voto import DelegacionVoto
    from .invitacion_piscina import InvitacionPiscina
    from .llave import Llave
    from .paquete import Paquete
    from .queja_mejora import QuejaMejora
    from .registro_piscina import RegistroPiscina
    from .ticket import Ticket


class Vecino(Base):
    __tablename__ = "vecinos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str | None] = mapped_column(String, nullable=True)
    telefono: Mapped[str | None] = mapped_column(String, nullable=True)
    piso: Mapped[str] = mapped_column(String, nullable=False)
    tipo: Mapped[str] = mapped_column(String, default="propietario")
    password: Mapped[str | None] = mapped_column(String, nullable=True)
    portal_activo: Mapped[str] = mapped_column(String, default="false")
    codigo_invitacion: Mapped[str | None] = mapped_column(String, nullable=True, unique=True)
    cargo: Mapped[str | None] = mapped_column(String, nullable=True)
    es_presidente: Mapped[bool] = mapped_column(Boolean, default=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    # Relaciones 1:N
    tickets: Mapped[list[Ticket]] = relationship(
        "Ticket",
        back_populates="vecino",
    )
    quejas_mejoras: Mapped[list[QuejaMejora]] = relationship(
        "QuejaMejora",
        back_populates="vecino",
    )
    registros_piscina: Mapped[list[RegistroPiscina]] = relationship(
        "RegistroPiscina",
        back_populates="vecino",
    )
    invitaciones_piscina: Mapped[list[InvitacionPiscina]] = relationship(
        "InvitacionPiscina",
        back_populates="vecino",
    )
    llaves: Mapped[list[Llave]] = relationship(
        "Llave",
        back_populates="vecino",
    )
    paquetes: Mapped[list[Paquete]] = relationship(
        "Paquete",
        back_populates="vecino",
    )

    # Relación 1:1 (unique=True en carnet_piscina.vecino_id)
    carnet_piscina: Mapped[CarnetPiscina | None] = relationship(
        "CarnetPiscina",
        back_populates="vecino",
    )

    # Relaciones de delegación (dos FKs en la misma tabla)
    delegaciones_delegante: Mapped[list[DelegacionVoto]] = relationship(
        "DelegacionVoto",
        foreign_keys="DelegacionVoto.vecino_delegante_id",
        back_populates="vecino_delegante",
    )
    delegaciones_delegado: Mapped[list[DelegacionVoto]] = relationship(
        "DelegacionVoto",
        foreign_keys="DelegacionVoto.vecino_delegado_id",
        back_populates="vecino_delegado",
    )
