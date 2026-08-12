from __future__ import annotations

from typing import TYPE_CHECKING

from database import Base
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .vecino import Vecino


class InvitacionPiscina(Base):
    __tablename__ = "invitaciones_piscina"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    vecino_id: Mapped[int] = mapped_column(ForeignKey("vecinos.id"), nullable=False)
    mes: Mapped[int] = mapped_column(Integer, nullable=False)
    anio: Mapped[int] = mapped_column(Integer, nullable=False)
    total_asignadas: Mapped[int] = mapped_column(Integer, default=10)
    usadas: Mapped[int] = mapped_column(Integer, default=0)

    # Relaciones
    vecino: Mapped[Vecino] = relationship(
        "Vecino",
        back_populates="invitaciones_piscina",
    )
