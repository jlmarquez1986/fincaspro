from database import get_db, utcnow
from fastapi import APIRouter, Depends, HTTPException
from models import Llave
from models.usuario import Usuario
from schemas import LlaveCreate, LlaveOut, LlavePrestamo
from security import get_current_user
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/", response_model=list[LlaveOut])
def listar_llaves(
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> list[Llave]:
    return db.query(Llave).order_by(Llave.codigo).all()


@router.post("/", response_model=LlaveOut, status_code=201)
def crear_llave(
    data: LlaveCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> Llave:
    if db.query(Llave).filter(Llave.codigo == data.codigo).first():
        raise HTTPException(status_code=400, detail="Código de llave ya existe")
    llave = Llave(**data.model_dump())
    db.add(llave)
    db.commit()
    db.refresh(llave)
    return llave


@router.patch("/{llave_id}/prestar", response_model=LlaveOut)
def prestar_llave(
    llave_id: int,
    data: LlavePrestamo,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> Llave:
    llave = db.query(Llave).filter(Llave.id == llave_id).first()
    if not llave:
        raise HTTPException(status_code=404, detail="Llave no encontrada")
    if llave.estado == "prestada":
        raise HTTPException(status_code=400, detail="La llave ya está prestada")
    llave.estado = "prestada"
    llave.prestada_a = data.prestada_a
    llave.vecino_id = data.vecino_id
    llave.desde = utcnow()
    db.commit()
    db.refresh(llave)
    return llave


@router.patch("/{llave_id}/devolver", response_model=LlaveOut)
def devolver_llave(
    llave_id: int,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> Llave:
    llave = db.query(Llave).filter(Llave.id == llave_id).first()
    if not llave:
        raise HTTPException(status_code=404, detail="Llave no encontrada")
    llave.estado = "disponible"
    llave.prestada_a = None
    llave.vecino_id = None
    llave.desde = None
    db.commit()
    db.refresh(llave)
    return llave


@router.delete("/{llave_id}", status_code=204)
def eliminar_llave(
    llave_id: int,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> None:
    llave = db.query(Llave).filter(Llave.id == llave_id).first()
    if not llave:
        raise HTTPException(status_code=404, detail="Llave no encontrada")
    db.delete(llave)
    db.commit()
