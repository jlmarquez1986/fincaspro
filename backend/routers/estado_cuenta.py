from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query
from models import EstadoCuenta
from models.usuario import Usuario
from schemas import EstadoCuentaCreate, EstadoCuentaOut
from security import get_current_user, role_required
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/", response_model=list[EstadoCuentaOut])
def listar_estados(
    entidad: str | None = Query(None),
    mes: int | None = Query(None),
    anio: int | None = Query(None),
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> list[EstadoCuenta]:
    q = db.query(EstadoCuenta)
    if entidad:
        q = q.filter(EstadoCuenta.entidad == entidad)
    if mes:
        q = q.filter(EstadoCuenta.mes == mes)
    if anio:
        q = q.filter(EstadoCuenta.anio == anio)
    return q.order_by(EstadoCuenta.anio.desc(), EstadoCuenta.mes.desc()).all()


@router.post("/", response_model=EstadoCuentaOut, status_code=201)
def crear_estado(
    data: EstadoCuentaCreate,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(role_required("admin")),
) -> EstadoCuenta:
    existente = (
        db.query(EstadoCuenta)
        .filter(
            EstadoCuenta.entidad == data.entidad,
            EstadoCuenta.mes == data.mes,
            EstadoCuenta.anio == data.anio,
        )
        .first()
    )
    if existente:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un estado para ese mes y año de esa entidad",
        )
    item = EstadoCuenta(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{item_id}", response_model=EstadoCuentaOut)
def actualizar_estado(
    item_id: int,
    data: EstadoCuentaCreate,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(role_required("admin")),
) -> EstadoCuenta:
    item = db.query(EstadoCuenta).filter(EstadoCuenta.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="No encontrado")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=204)
def eliminar_estado(
    item_id: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(role_required("admin")),
) -> None:
    item = db.query(EstadoCuenta).filter(EstadoCuenta.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="No encontrado")
    db.delete(item)
    db.commit()
