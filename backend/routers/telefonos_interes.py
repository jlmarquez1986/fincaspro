from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query
from models import TelefonoInteres
from models.usuario import Usuario
from schemas import TelefonoInteresCreate, TelefonoInteresOut
from security import get_current_user, role_required
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/", response_model=list[TelefonoInteresOut])
def listar_telefonos(
    categoria: str | None = Query(None),
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> list[TelefonoInteres]:
    q = db.query(TelefonoInteres)
    if categoria:
        q = q.filter(TelefonoInteres.categoria == categoria)
    return q.order_by(TelefonoInteres.nombre).all()


@router.post("/", response_model=TelefonoInteresOut, status_code=201)
def crear_telefono(
    data: TelefonoInteresCreate,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(role_required("admin")),
) -> TelefonoInteres:
    item = TelefonoInteres(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{item_id}", response_model=TelefonoInteresOut)
def actualizar_telefono(
    item_id: int,
    data: TelefonoInteresCreate,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(role_required("admin")),
) -> TelefonoInteres:
    item = db.query(TelefonoInteres).filter(TelefonoInteres.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="No encontrado")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=204)
def eliminar_telefono(
    item_id: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(role_required("admin")),
) -> None:
    item = db.query(TelefonoInteres).filter(TelefonoInteres.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="No encontrado")
    db.delete(item)
    db.commit()
