import secrets
from datetime import datetime

from database import get_db, utcnow
from fastapi import APIRouter, Depends, HTTPException, Query
from models import CarnetPiscina, Configuracion, InvitacionPiscina, RegistroPiscina, Vecino
from models.usuario import Usuario
from schemas import (
    CarnetPiscinaCreate,
    CarnetPiscinaOut,
    RegistroPiscinaCreate,
    RegistroPiscinaOut,
)
from security import get_current_user, role_required
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/carnets", response_model=list[CarnetPiscinaOut])
def listar_carnets(
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> list[CarnetPiscina]:
    return db.query(CarnetPiscina).all()


@router.post("/carnets", response_model=CarnetPiscinaOut, status_code=201)
def crear_carnet(
    data: CarnetPiscinaCreate,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(role_required("admin")),
) -> CarnetPiscina:
    vecino = db.query(Vecino).filter(Vecino.id == data.vecino_id).first()
    if not vecino:
        raise HTTPException(status_code=400, detail="Vecino no existe")
    numero = data.numero_carnet or f"P-{secrets.token_hex(4).upper()}"
    if db.query(CarnetPiscina).filter(CarnetPiscina.numero_carnet == numero).first():
        raise HTTPException(status_code=400, detail="Número de carnet ya existe")
    carnet = CarnetPiscina(**data.model_dump(exclude={"numero_carnet"}), numero_carnet=numero)
    db.add(carnet)
    db.commit()
    db.refresh(carnet)
    return carnet


@router.get("/carnets/verificar/{numero}")
def verificar_carnet(
    numero: str,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> dict[str, object]:
    carnet = db.query(CarnetPiscina).filter(CarnetPiscina.numero_carnet == numero).first()
    if not carnet:
        raise HTTPException(status_code=404, detail="Carnet no válido")
    if not carnet.activo:
        raise HTTPException(status_code=403, detail="Carnet desactivado")
    vecino = db.query(Vecino).filter(Vecino.id == carnet.vecino_id).first()
    if not vecino:
        raise HTTPException(status_code=404, detail="Vecino no encontrado")
    return {
        "valido": True,
        "vecino_id": vecino.id,
        "nombre": vecino.nombre,
        "piso": vecino.piso,
        "carnet": carnet.numero_carnet,
    }


@router.get("/invitaciones/vecino/{vecino_id}")
def saldo_invitaciones(
    vecino_id: int,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> dict[str, int]:
    hoy = utcnow()
    mes = hoy.month
    anio = hoy.year
    inv = (
        db.query(InvitacionPiscina)
        .filter(
            InvitacionPiscina.vecino_id == vecino_id,
            InvitacionPiscina.mes == mes,
            InvitacionPiscina.anio == anio,
        )
        .first()
    )
    if not inv:
        config = (
            db.query(Configuracion).filter(Configuracion.clave == "invitaciones_mensuales").first()
        )
        total_default = int(config.valor) if config else 10
        inv = InvitacionPiscina(
            vecino_id=vecino_id,
            mes=mes,
            anio=anio,
            total_asignadas=total_default,
            usadas=0,
        )
        db.add(inv)
        db.commit()
        db.refresh(inv)
    return {
        "total": inv.total_asignadas,
        "usadas": inv.usadas,
        "disponibles": inv.total_asignadas - inv.usadas,
        "mes": mes,
        "anio": anio,
    }


@router.patch("/invitaciones/config")
def configurar_invitaciones(
    nuevo_total: int = Query(..., ge=0),
    db: Session = Depends(get_db),
    admin: Usuario = Depends(role_required("admin")),
) -> dict[str, str]:
    config = db.query(Configuracion).filter(Configuracion.clave == "invitaciones_mensuales").first()
    if not config:
        config = Configuracion(
            clave="invitaciones_mensuales",
            valor=str(nuevo_total),
            descripcion="Número de invitaciones por vecino al mes",
        )
        db.add(config)
    else:
        config.valor = str(nuevo_total)
    db.commit()
    return {"mensaje": f"Configurado a {nuevo_total} invitaciones/mes"}


@router.post("/registros", response_model=RegistroPiscinaOut, status_code=201)
def registrar_acceso(
    data: RegistroPiscinaCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(role_required("admin", "conserje", "socorrista")),
) -> RegistroPiscina:
    vecino = db.query(Vecino).filter(Vecino.id == data.vecino_id).first()
    if not vecino:
        raise HTTPException(status_code=400, detail="Vecino no existe")
    carnet = (
        db.query(CarnetPiscina)
        .filter(
            CarnetPiscina.vecino_id == data.vecino_id,
            CarnetPiscina.activo.is_(True),
        )
        .first()
    )
    if not carnet:
        raise HTTPException(status_code=403, detail="Vecino no tiene carnet activo")

    if data.tipo == "invitacion":
        hoy = utcnow()
        inv = (
            db.query(InvitacionPiscina)
            .filter(
                InvitacionPiscina.vecino_id == data.vecino_id,
                InvitacionPiscina.mes == hoy.month,
                InvitacionPiscina.anio == hoy.year,
            )
            .first()
        )
        if not inv:
            config = (
                db.query(Configuracion)
                .filter(Configuracion.clave == "invitaciones_mensuales")
                .first()
            )
            total_default = int(config.valor) if config else 10
            inv = InvitacionPiscina(
                vecino_id=data.vecino_id,
                mes=hoy.month,
                anio=hoy.year,
                total_asignadas=total_default,
                usadas=0,
            )
            db.add(inv)
        if inv.usadas >= inv.total_asignadas:
            raise HTTPException(
                status_code=400, detail="Sin invitaciones disponibles para este mes"
            )
        inv.usadas += 1

    registro = RegistroPiscina(
        vecino_id=data.vecino_id,
        tipo=data.tipo,
        nombre_invitado=data.nombre_invitado,
        registrado_por=user.id,
    )
    db.add(registro)
    db.commit()
    db.refresh(registro)
    return registro


@router.get("/registros", response_model=list[RegistroPiscinaOut])
def listar_registros(
    vecino_id: int | None = Query(None),
    desde: datetime | None = Query(None),
    hasta: datetime | None = Query(None),
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> list[RegistroPiscina]:
    q = db.query(RegistroPiscina)
    if vecino_id:
        q = q.filter(RegistroPiscina.vecino_id == vecino_id)
    if desde:
        q = q.filter(RegistroPiscina.fecha_hora >= desde)
    if hasta:
        q = q.filter(RegistroPiscina.fecha_hora <= hasta)
    return q.order_by(RegistroPiscina.fecha_hora.desc()).all()
