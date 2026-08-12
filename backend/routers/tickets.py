import logging
import os
import shutil
import uuid

from database import get_db
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile
from models import Comentario, Ticket, Vecino
from models.usuario import Usuario
from rate_limiter import limiter
from schemas import ComentarioCreate, ComentarioOut, TicketOut, TicketUpdate
from security import get_current_user, role_required
from services.email_service import notify_new_ticket, notify_ticket_status_change
from sqlalchemy.orm import Session
from upload_utils import validar_imagen

logger = logging.getLogger(__name__)
router = APIRouter()

UPLOAD_DIR = "uploads/tickets"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/", response_model=list[TicketOut])
def listar_tickets(
    estado: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> list[Ticket]:
    q = db.query(Ticket)
    if current_user.rol == "vecino":
        q = q.filter(Ticket.vecino_id == current_user.id)
    if estado:
        q = q.filter(Ticket.estado == estado)
    return q.order_by(Ticket.creado_en.desc()).offset(skip).limit(limit).all()


@router.post("/", response_model=TicketOut, status_code=201)
@limiter.limit("10/minute")
async def crear_ticket(
    request: Request,
    asunto: str = Form(...),
    descripcion: str | None = Form(None),
    categoria: str = Form("otros"),
    prioridad: str = Form("normal"),
    piso: str | None = Form(None),
    vecino_id: int | None = Form(None),
    asignado_a: str | None = Form(None),
    alcance: str | None = Form(None),
    foto: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> Ticket:
    if vecino_id:
        vecino = db.query(Vecino).filter(Vecino.id == vecino_id).first()
        if not vecino:
            raise HTTPException(status_code=400, detail="El vecino especificado no existe")

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
        piso=piso,
        vecino_id=vecino_id,
        asignado_a=asignado_a,
        alcance=alcance,
        foto_path=foto_path,
        estado="pendiente",
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    # Notificación por email
    if vecino_id:
        vecino = db.query(Vecino).filter(Vecino.id == vecino_id).first()
        if vecino and vecino.email:
            try:
                await notify_new_ticket(ticket, vecino.email)
            except Exception as e:
                logger.warning(
                    "No se pudo notificar nuevo ticket %s a %s: %s",
                    ticket.id,
                    vecino.email,
                    e,
                )

    return ticket


@router.patch("/{ticket_id}", response_model=TicketOut)
async def actualizar_ticket(
    ticket_id: int,
    data: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> Ticket:
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    if current_user.rol == "vecino" and ticket.vecino_id != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado")

    old_status = ticket.estado
    update_data = data.model_dump(exclude_none=True)

    for k, v in update_data.items():
        setattr(ticket, k, v)

    db.commit()
    db.refresh(ticket)

    # Notificar cambio de estado
    if "estado" in update_data and old_status != ticket.estado:
        if ticket.vecino_id:
            vecino = db.query(Vecino).filter(Vecino.id == ticket.vecino_id).first()
            if vecino and vecino.email:
                try:
                    await notify_ticket_status_change(ticket, vecino.email, old_status)
                except Exception as e:
                    logger.warning(
                        "No se pudo notificar cambio de estado del ticket %s: %s",
                        ticket.id,
                        e,
                    )

    return ticket


@router.delete("/{ticket_id}", status_code=204)
def eliminar_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(role_required("admin")),
) -> None:
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    if ticket.foto_path:
        full_path = ticket.foto_path.lstrip("/")
        if os.path.exists(full_path):
            os.remove(full_path)

    db.delete(ticket)
    db.commit()


@router.post("/{ticket_id}/comentarios", response_model=ComentarioOut, status_code=201)
def agregar_comentario(
    ticket_id: int,
    data: ComentarioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> Comentario:
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    if current_user.rol == "vecino" and ticket.vecino_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="No tienes permiso para comentar en este ticket"
        )

    comentario = Comentario(
        ticket_id=ticket_id,
        autor=current_user.nombre,
        texto=data.texto,
    )
    db.add(comentario)
    db.commit()
    db.refresh(comentario)
    return comentario
