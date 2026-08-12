"""
Portal del Vecino — Endpoints exclusivos para vecinos autenticados.
Los vecinos solo pueden ver sus propios datos: tickets, paquetes y avisos.
"""

import os
import shutil
import uuid

from database import get_db
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from models import Aviso, Paquete, Ticket, Vecino
from schemas import AvisoOut, PaqueteOut, TicketOut, VecinoLogin, VecinoToken
from security import create_access_token, get_current_vecino, verify_password
from sqlalchemy.orm import Session
from upload_utils import validar_imagen

router = APIRouter()

UPLOAD_DIR = "uploads/tickets"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/login", response_model=VecinoToken)
def portal_login(
    data: VecinoLogin,
    db: Session = Depends(get_db),
) -> dict[str, object]:
    """Login exclusivo para vecinos del portal."""
    vecino = db.query(Vecino).filter(Vecino.email == data.email).first()
    if not vecino or not vecino.password:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    if not verify_password(data.password, vecino.password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    if vecino.portal_activo != "true":
        raise HTTPException(status_code=403, detail="Cuenta de portal no activada")

    token = create_access_token({"vecino_id": vecino.id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "vecino": {
            "id": vecino.id,
            "nombre": vecino.nombre,
            "piso": vecino.piso,
        },
    }


@router.get("/me")
def mi_perfil(
    vecino: Vecino = Depends(get_current_vecino),
) -> dict[str, object]:
    """Obtener datos del vecino logueado."""
    return {
        "id": vecino.id,
        "nombre": vecino.nombre,
        "email": vecino.email,
        "telefono": vecino.telefono,
        "piso": vecino.piso,
        "tipo": vecino.tipo,
    }


@router.get("/mis-tickets", response_model=list[TicketOut])
def mis_tickets(
    db: Session = Depends(get_db),
    vecino: Vecino = Depends(get_current_vecino),
) -> list[Ticket]:
    """Ver solo los tickets del vecino logueado."""
    return (
        db.query(Ticket)
        .filter(Ticket.vecino_id == vecino.id)
        .order_by(Ticket.creado_en.desc())
        .all()
    )


@router.post("/tickets", response_model=TicketOut, status_code=201)
def reportar_averia(
    asunto: str = Form(...),
    descripcion: str | None = Form(None),
    categoria: str = Form("otros"),
    prioridad: str = Form("normal"),
    foto: UploadFile = File(None),
    db: Session = Depends(get_db),
    vecino: Vecino = Depends(get_current_vecino),
) -> Ticket:
    """
    El vecino reporta su propia avería desde el portal.
    vecino_id y piso se asignan automáticamente desde la sesión.
    """
    foto_path = None
    if foto and foto.filename:
        validar_imagen(foto)
        ext = os.path.splitext(foto.filename)[1].lower()
        filename = f"{uuid.uuid4()}{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(foto.file, buffer)
        foto_path = f"/uploads/tickets/{filename}"

    ticket = Ticket(
        asunto=asunto,
        descripcion=descripcion,
        categoria=categoria,
        prioridad=prioridad,
        foto_path=foto_path,
        piso=vecino.piso,
        vecino_id=vecino.id,
        estado="pendiente",
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.get("/mis-paquetes", response_model=list[PaqueteOut])
def mis_paquetes(
    db: Session = Depends(get_db),
    vecino: Vecino = Depends(get_current_vecino),
) -> list[Paquete]:
    """Ver solo los paquetes del vecino logueado."""
    return (
        db.query(Paquete)
        .filter(Paquete.vecino_id == vecino.id)
        .order_by(Paquete.recibido_en.desc())
        .all()
    )


@router.get("/avisos", response_model=list[AvisoOut])
def avisos_comunidad(
    db: Session = Depends(get_db),
    vecino: Vecino = Depends(get_current_vecino),
) -> list[Aviso]:
    """Ver avisos activos de la comunidad."""
    return db.query(Aviso).filter(Aviso.activo == "true").order_by(Aviso.creado_en.desc()).all()
