from typing import Any

from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from models.usuario import Usuario
from models.vecino import Vecino
from rate_limiter import limiter
from security import create_access_token, verify_password
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/login")
@limiter.limit("5/minute")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    user = db.query(Usuario).filter(Usuario.username == form_data.username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    token = create_access_token(data={"sub": user.username})
    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": {
            "id": user.id,
            "nombre": user.nombre,
            "username": user.username,
            "email": user.email,
            "rol": user.rol,
        },
    }


@router.post("/vecinos/login")
@limiter.limit("5/minute")
def login_vecino(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    vecino = db.query(Vecino).filter(Vecino.email == form_data.username).first()
    if vecino is None or vecino.password is None:
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")
    if not verify_password(form_data.password, vecino.password):
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")
    token = create_access_token(data={"vecino_id": vecino.id})
    return {"access_token": token, "token_type": "bearer"}
