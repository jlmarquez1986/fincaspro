"""
backend/security.py — Utilidades de autenticación (JWT + bcrypt + dependencias).

Usa bcrypt directamente (sin passlib) para máxima compatibilidad
con Python 3.13 y versiones modernas de bcrypt.
"""

import os
import secrets
from collections.abc import Callable
from datetime import timedelta
from typing import Any, cast

import bcrypt
from database import get_db, utcnow
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from models.usuario import Usuario
from models.vecino import Vecino
from sqlalchemy.orm import Session

# ------------------------------------------------------------------
# Configuración
# ------------------------------------------------------------------
ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
SECRET_KEY_RAW: str | None = os.getenv("SECRET_KEY")

if not SECRET_KEY_RAW:
    if ENVIRONMENT == "production":
        raise RuntimeError(
            "SECRET_KEY no está definido. En producción es obligatorio "
            "fijarlo como variable de entorno (ver .env.example)."
        )
    SECRET_KEY_RAW = secrets.token_hex(32)

SECRET_KEY: str = SECRET_KEY_RAW
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))
MIN_PASSWORD_LENGTH: int = 8

# tokenUrl para documentación Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


# ------------------------------------------------------------------
# Hashing de contraseñas
# ------------------------------------------------------------------
def hash_password(password: str) -> str:
    """Hashea una contraseña con bcrypt."""
    if not password or len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"La contraseña debe tener al menos {MIN_PASSWORD_LENGTH} caracteres")
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña contra su hash bcrypt."""
    if not hashed_password:
        return False
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        # Hash inválido (texto plano, formato antiguo, etc.)
        return False


# ------------------------------------------------------------------
# JWT
# ------------------------------------------------------------------
def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Genera un JWT de acceso."""
    to_encode = data.copy()
    expire = utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode["exp"] = expire
    return cast(str, jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM))


def _decode_token(token: str) -> dict[str, Any]:
    try:
        return cast(dict[str, Any], jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]))
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas o token expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ------------------------------------------------------------------
# Dependencias FastAPI
# ------------------------------------------------------------------
def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    """Dependencia para endpoints del panel de administración (Usuario)."""
    if not token:
        raise HTTPException(status_code=401, detail="No autenticado")
    payload = _decode_token(token)
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Token inválido")
    user = db.query(Usuario).filter(Usuario.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return user


def get_current_vecino(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Vecino:
    """Dependencia para el Portal del Vecino."""
    if not token:
        raise HTTPException(status_code=401, detail="No autenticado")
    payload = _decode_token(token)
    vecino_id = payload.get("vecino_id")
    if vecino_id is None:
        raise HTTPException(status_code=401, detail="Token inválido")
    vecino = db.query(Vecino).filter(Vecino.id == vecino_id).first()
    if not vecino:
        raise HTTPException(status_code=401, detail="Vecino no encontrado")
    return vecino


def role_required(*roles: str) -> Callable[..., Usuario]:
    """Fábrica de dependencias: role_required('admin'), role_required('admin', 'conserje'), etc."""

    def dependency(user: Usuario = Depends(get_current_user)) -> Usuario:
        if user.rol not in roles:
            raise HTTPException(status_code=403, detail="No tienes permisos suficientes")
        return user

    return dependency
