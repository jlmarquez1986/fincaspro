import logging

from database import get_db, utcnow
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from models import Paquete, Vecino
from models.usuario import Usuario
from rate_limiter import limiter
from schemas import PaqueteCreate, PaqueteOut
from security import get_current_user
from services.email_service import notify_new_package
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=list[PaqueteOut])
def listar_paquetes(
    estado: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> list[Paquete]:
    q = db.query(Paquete)
    if estado:
        q = q.filter(Paquete.estado == estado)
    return q.order_by(Paquete.recibido_en.desc()).offset(skip).limit(limit).all()


@router.post("/", response_model=PaqueteOut, status_code=201)
@limiter.limit("10/minute")
async def registrar_paquete(
    request: Request,
    data: PaqueteCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> Paquete:
    pkg = Paquete(**data.model_dump())
    db.add(pkg)
    db.commit()
    db.refresh(pkg)

    vecino = db.query(Vecino).filter(Vecino.id == pkg.vecino_id).first()
    if vecino and vecino.email:
        try:
            await notify_new_package(pkg, vecino.email, vecino.nombre)
        except Exception:
            logger.warning(
                "No se pudo enviar el email de nuevo paquete (id=%s)",
                pkg.id,
                exc_info=True,
            )

    return pkg


@router.patch("/{pkg_id}/entregar", response_model=PaqueteOut)
def marcar_entregado(
    pkg_id: int,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> Paquete:
    pkg = db.query(Paquete).filter(Paquete.id == pkg_id).first()
    if not pkg:
        raise HTTPException(status_code=404, detail="Paquete no encontrado")
    pkg.estado = "entregado"
    pkg.entregado_en = utcnow()
    db.commit()
    db.refresh(pkg)
    return pkg


@router.delete("/{pkg_id}", status_code=204)
def eliminar_paquete(
    pkg_id: int,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> None:
    pkg = db.query(Paquete).filter(Paquete.id == pkg_id).first()
    if not pkg:
        raise HTTPException(status_code=404, detail="Paquete no encontrado")
    db.delete(pkg)
    db.commit()
