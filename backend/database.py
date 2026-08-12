from __future__ import annotations

import os
from collections.abc import Generator
from datetime import UTC, datetime

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fincaspro.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base declarativa moderna de SQLAlchemy 2.0.

    Reemplaza a ``declarative_base()`` de SQLAlchemy 1.x.
    Permite tipado estricto y es compatible con ``Mapped``.
    """

    pass


def utcnow() -> datetime:
    """Sustituto de datetime.utcnow() (obsoleto desde Python 3.12).

    Devuelve un datetime *naive* en UTC, manteniendo la convención
    de almacenamiento del proyecto.
    """
    return datetime.now(UTC).replace(tzinfo=None)


def get_db() -> Generator[Session]:
    """Generador de sesiones para FastAPI Depends."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
