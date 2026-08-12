from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from models import Usuario
from rate_limiter import limiter
from schemas import UsuarioCreate, UsuarioOut, UsuarioUpdate
from security import hash_password, role_required
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/", response_model=list[UsuarioOut])
def listar_usuarios(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    user: Usuario = Depends(role_required("admin")),
) -> list[Usuario]:
    return db.query(Usuario).offset(skip).limit(limit).all()


@router.post("/", response_model=UsuarioOut, status_code=201)
@limiter.limit("5/minute")
def crear_usuario(
    request: Request,
    data: UsuarioCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(role_required("admin")),
) -> Usuario:
    if db.query(Usuario).filter(Usuario.username == data.username).first():
        raise HTTPException(status_code=400, detail="Nombre de usuario ya existe")
    if db.query(Usuario).filter(Usuario.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email ya registrado")
    hashed = hash_password(data.password)
    usuario = Usuario(
        nombre=data.nombre,
        username=data.username,
        email=data.email,
        password=hashed,
        rol=data.rol or "conserje",
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.patch("/{usuario_id}", response_model=UsuarioOut)
def actualizar_usuario(
    usuario_id: int,
    data: UsuarioUpdate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(role_required("admin")),
) -> Usuario:
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    for k, v in data.model_dump(exclude_none=True).items():
        if k == "password" and v:
            v = hash_password(v)
        setattr(usuario, k, v)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.delete("/{usuario_id}", status_code=204)
def eliminar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    user: Usuario = Depends(role_required("admin")),
) -> None:
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(usuario)
    db.commit()
