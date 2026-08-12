import logging

from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from models import Aviso, Vecino
from models.usuario import Usuario
from rate_limiter import limiter
from schemas import AvisoCreate, AvisoOut
from security import get_current_user
from services.email_service import notify_new_aviso
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=list[AvisoOut])
def listar_avisos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> list[Aviso]:
    return (
        db.query(Aviso)
        .filter(Aviso.activo == "true")
        .order_by(Aviso.creado_en.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.post("/", response_model=AvisoOut, status_code=201)
@limiter.limit("5/minute")
async def crear_aviso(
    request: Request,
    data: AvisoCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> Aviso:
    aviso = Aviso(**data.model_dump())
    db.add(aviso)
    db.commit()
    db.refresh(aviso)

    vecinos = db.query(Vecino).filter(Vecino.email.isnot(None)).all()
    for vecino in vecinos:
        if vecino.email:
            try:
                await notify_new_aviso(aviso, vecino.email)
            except Exception:
                logger.warning(
                    "No se pudo notificar el aviso %s a %s",
                    aviso.id,
                    vecino.email,
                    exc_info=True,
                )

    return aviso


@router.patch("/{aviso_id}/archivar")
def archivar_aviso(
    aviso_id: int,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> dict[str, str]:
    aviso = db.query(Aviso).filter(Aviso.id == aviso_id).first()
    if not aviso:
        raise HTTPException(status_code=404, detail="Aviso no encontrado")
    aviso.activo = "false"
    db.commit()
    return {"mensaje": "Aviso archivado"}
