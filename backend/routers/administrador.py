from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query
from models import Administrador
from models.usuario import Usuario
from schemas import AdministradorCreate, AdministradorOut
from security import get_current_user, role_required
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/", response_model=list[AdministradorOut])
def listar_administradores(
    entidad: str | None = Query(None),
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> list[Administrador]:
    q = db.query(Administrador)
    if entidad:
        q = q.filter(Administrador.entidad == entidad)
    return q.all()


@router.post("/", response_model=AdministradorOut, status_code=201)
def crear_administrador(
    data: AdministradorCreate,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(role_required("admin")),
) -> Administrador:
    item = Administrador(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{item_id}", response_model=AdministradorOut)
def actualizar_administrador(
    item_id: int,
    data: AdministradorCreate,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(role_required("admin")),
) -> Administrador:
    item = db.query(Administrador).filter(Administrador.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="No encontrado")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=204)
def eliminar_administrador(
    item_id: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(role_required("admin")),
) -> None:
    item = db.query(Administrador).filter(Administrador.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="No encontrado")
    db.delete(item)
    db.commit()
