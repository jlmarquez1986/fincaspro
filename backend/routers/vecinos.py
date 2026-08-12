import secrets
import string

from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from models import Vecino
from models.usuario import Usuario
from rate_limiter import limiter
from schemas import VecinoCreate, VecinoOut, VecinoPortalCreate, VecinoUpdate
from security import get_current_user, hash_password, role_required
from sqlalchemy.orm import Session

router = APIRouter()


def generar_codigo_invitacion() -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(6))


@router.get("/", response_model=list[VecinoOut])
def listar_vecinos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> list[Vecino]:
    return db.query(Vecino).order_by(Vecino.piso).offset(skip).limit(limit).all()


@router.post("/", response_model=VecinoOut, status_code=201)
def crear_vecino(
    data: VecinoCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(role_required("admin")),
) -> Vecino:
    codigo = generar_codigo_invitacion()
    while db.query(Vecino).filter(Vecino.codigo_invitacion == codigo).first():
        codigo = generar_codigo_invitacion()
    vecino = Vecino(**data.model_dump())
    vecino.codigo_invitacion = codigo
    db.add(vecino)
    db.commit()
    db.refresh(vecino)
    return vecino


@router.get("/{vecino_id}", response_model=VecinoOut)
def obtener_vecino(
    vecino_id: int,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> Vecino:
    v = db.query(Vecino).filter(Vecino.id == vecino_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vecino no encontrado")
    return v


@router.patch("/{vecino_id}", response_model=VecinoOut)
def actualizar_vecino(
    vecino_id: int,
    data: VecinoUpdate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(role_required("admin")),
) -> Vecino:
    vecino = db.query(Vecino).filter(Vecino.id == vecino_id).first()
    if not vecino:
        raise HTTPException(status_code=404, detail="Vecino no encontrado")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(vecino, k, v)
    db.commit()
    db.refresh(vecino)
    return vecino


@router.delete("/{vecino_id}", status_code=204)
def eliminar_vecino(
    vecino_id: int,
    db: Session = Depends(get_db),
    user: Usuario = Depends(role_required("admin")),
) -> None:
    v = db.query(Vecino).filter(Vecino.id == vecino_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vecino no encontrado")
    db.delete(v)
    db.commit()


@router.post("/portal/registro", response_model=dict, status_code=201)
@limiter.limit("3/minute")
def registro_portal(
    request: Request,
    data: VecinoPortalCreate,
    db: Session = Depends(get_db),
) -> dict[str, str | int]:
    vecino = (
        db.query(Vecino)
        .filter(
            Vecino.piso == data.piso,
            Vecino.codigo_invitacion == data.codigo_invitacion,
        )
        .first()
    )
    if not vecino:
        raise HTTPException(status_code=400, detail="Piso o código de invitación inválido")
    if vecino.portal_activo == "true":
        raise HTTPException(
            status_code=400, detail="Este piso ya tiene una cuenta de portal activa"
        )

    vecino.nombre = data.nombre
    vecino.email = data.email
    try:
        vecino.password = hash_password(data.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    vecino.portal_activo = "true"
    vecino.codigo_invitacion = None  # invalidar
    db.commit()
    db.refresh(vecino)

    return {
        "mensaje": "Cuenta de portal activada correctamente",
        "vecino_id": vecino.id,
    }
