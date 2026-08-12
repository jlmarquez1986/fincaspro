from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query
from models import DelegacionVoto, Vecino
from models.usuario import Usuario
from schemas import DelegacionVotoCreate, DelegacionVotoOut
from security import get_current_user
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/", response_model=list[DelegacionVotoOut])
def listar_delegaciones(
    activa: bool | None = Query(None),
    vecino_id: int | None = Query(None),
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> list[DelegacionVoto]:
    q = db.query(DelegacionVoto)
    if user.rol == "vecino":
        q = q.filter(DelegacionVoto.vecino_delegante_id == user.id)
    else:
        if vecino_id is not None:
            q = q.filter(DelegacionVoto.vecino_delegante_id == vecino_id)
    if activa is not None:
        q = q.filter(DelegacionVoto.activa == activa)
    return q.order_by(DelegacionVoto.fecha.desc()).all()


@router.post("/", response_model=DelegacionVotoOut, status_code=201)
def crear_delegacion(
    data: DelegacionVotoCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> DelegacionVoto:
    delegante = db.query(Vecino).filter(Vecino.id == data.vecino_delegante_id).first()
    delegado = db.query(Vecino).filter(Vecino.id == data.vecino_delegado_id).first()
    if not delegante or not delegado:
        raise HTTPException(status_code=400, detail="Vecino no válido")
    if user.rol != "admin" and user.id != delegante.id:
        raise HTTPException(status_code=403, detail="No puedes delegar en nombre de otro vecino")
    if delegante.id == delegado.id:
        raise HTTPException(status_code=400, detail="No puedes delegar en ti mismo")
    item = DelegacionVoto(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{item_id}/desactivar")
def desactivar_delegacion(
    item_id: int,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> dict[str, str]:
    item = db.query(DelegacionVoto).filter(DelegacionVoto.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="No encontrado")
    if user.rol != "admin" and user.id != item.vecino_delegante_id:
        raise HTTPException(status_code=403, detail="No autorizado")
    item.activa = False
    db.commit()
    return {"mensaje": "Delegación desactivada"}
