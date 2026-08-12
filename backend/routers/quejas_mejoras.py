import os
import shutil
import uuid

from database import get_db
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from models import QuejaMejora
from models.usuario import Usuario
from schemas import QuejaMejoraOut, QuejaMejoraUpdate
from security import get_current_user, role_required
from sqlalchemy.orm import Session
from upload_utils import validar_imagen

router = APIRouter()

UPLOAD_DIR = "uploads/quejas"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/", response_model=list[QuejaMejoraOut])
def listar_quejas_mejoras(
    tipo: str | None = Query(None),
    categoria: str | None = Query(None),
    estado: str | None = Query(None),
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> list[QuejaMejora]:
    q = db.query(QuejaMejora)
    if tipo:
        q = q.filter(QuejaMejora.tipo == tipo)
    if categoria:
        q = q.filter(QuejaMejora.categoria == categoria)
    if estado:
        q = q.filter(QuejaMejora.estado == estado)
    return q.order_by(QuejaMejora.creado_en.desc()).all()


@router.post("/", response_model=QuejaMejoraOut, status_code=201)
async def crear_queja_mejora(
    tipo: str = Form(...),
    categoria: str = Form(...),
    asunto: str = Form(...),
    descripcion: str | None = Form(None),
    prioridad: str = Form("media"),
    vecino_id: int | None = Form(None),
    foto: UploadFile = File(None),
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> QuejaMejora:
    foto_path = None
    if foto and foto.filename:
        validar_imagen(foto)
        ext = os.path.splitext(foto.filename)[1].lower()
        filename = f"{uuid.uuid4()}{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(foto.file, buffer)
        foto_path = f"/uploads/quejas/{filename}"

    item = QuejaMejora(
        tipo=tipo,
        categoria=categoria,
        asunto=asunto,
        descripcion=descripcion,
        prioridad=prioridad,
        vecino_id=vecino_id,
        creado_por=user.id,
        foto_path=foto_path,
        estado="pendiente",
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{item_id}", response_model=QuejaMejoraOut)
def actualizar_queja_mejora(
    item_id: int,
    data: QuejaMejoraUpdate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> QuejaMejora:
    item = db.query(QuejaMejora).filter(QuejaMejora.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="No encontrado")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=204)
def eliminar_queja_mejora(
    item_id: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(role_required("admin")),
) -> None:
    item = db.query(QuejaMejora).filter(QuejaMejora.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="No encontrado")
    db.delete(item)
    db.commit()
