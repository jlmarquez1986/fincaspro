import os

from database import get_db
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from rate_limiter import limiter
from routers import (
    administrador,
    auth,
    avisos,
    delegacion_voto,
    estado_cuenta,
    llaves,
    paqueteria,
    piscina,
    portal,
    quejas_mejoras,
    telefonos_interes,
    tickets,
    usuarios,
    vecinos,
)
from security import get_current_user
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy.orm import Session

ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()

# En desarrollo se permite crear el esquema automáticamente para facilitar el trabajo local.
# En producción el esquema lo gestiona exclusivamente Alembic al arrancar el contenedor.
if ENVIRONMENT != "production":
    from database import Base, engine

    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FincasPro API",
    description="Sistema Integral de Gestión de Fincas y Conserjería",
    version="2.0.0",
)

# Configurar rate limiting
app.state.limiter = limiter
# slowapi tipa su handler de forma distinta a la que espera Starlette
# (desajuste de stubs entre librerías, no un error real): se ignora aquí.
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,  # type: ignore[arg-type]
)

# CORS configurable por entorno. En producción se recomienda permitir únicamente
# el/los dominios públicos reales de la aplicación.
_cors_origins_raw = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://localhost",
)
CORS_ORIGINS = [origin.strip() for origin in _cors_origins_raw.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticación"])
app.include_router(usuarios.router, prefix="/api/usuarios", tags=["Usuarios"])
app.include_router(vecinos.router, prefix="/api/vecinos", tags=["Vecinos"])
app.include_router(tickets.router, prefix="/api/tickets", tags=["Tickets"])
app.include_router(paqueteria.router, prefix="/api/paqueteria", tags=["Paquetería"])
app.include_router(llaves.router, prefix="/api/llaves", tags=["Llaves"])
app.include_router(avisos.router, prefix="/api/avisos", tags=["Avisos"])
app.include_router(portal.router, prefix="/api/portal", tags=["Portal Vecino"])

# Nuevos routers
app.include_router(quejas_mejoras.router, prefix="/api/quejas-mejoras", tags=["Quejas y Mejoras"])
app.include_router(piscina.router, prefix="/api/piscina", tags=["Piscina"])
app.include_router(administrador.router, prefix="/api/administradores", tags=["Administradores"])
app.include_router(estado_cuenta.router, prefix="/api/estados-cuenta", tags=["Estados de Cuenta"])
app.include_router(
    delegacion_voto.router, prefix="/api/delegaciones-voto", tags=["Delegaciones de Voto"]
)
app.include_router(
    telefonos_interes.router, prefix="/api/telefonos-interes", tags=["Teléfonos de Interés"]
)


@app.get("/health", tags=["Health"])
def health_check():
    """Endpoint ligero para Docker y sistemas de monitorización."""
    return {"status": "ok", "service": "fincaspro-api"}


@app.get("/api/config", tags=["Config"])
def get_public_config():
    return {
        "community_name": os.getenv("COMMUNITY_NAME", "Comunidad"),
    }


@app.get("/api/dashboard", tags=["Dashboard"])
def get_dashboard_stats(db: Session = Depends(get_db), _=Depends(get_current_user)):
    from models.llave import Llave
    from models.paquete import Paquete
    from models.ticket import Ticket

    tickets_abiertos = db.query(Ticket).filter(Ticket.estado != "resuelto").count()
    pkgs_pendientes = db.query(Paquete).filter(Paquete.estado == "pendiente").count()
    llaves_prestadas = db.query(Llave).filter(Llave.estado == "prestada").count()
    tickets_resueltos = db.query(Ticket).filter(Ticket.estado == "resuelto").count()
    return {
        "tickets_abiertos": tickets_abiertos,
        "pkgs_pendientes": pkgs_pendientes,
        "llaves_prestadas": llaves_prestadas,
        "tickets_resueltos": tickets_resueltos,
    }


@app.get("/", tags=["Root"])
def root():
    return {
        "mensaje": "FincasPro API v2.0 activa 🏢",
        "docs": "/docs",
        "features": [
            "Notificaciones por email",
            "Subida de fotos en tickets",
            "Portal del vecino",
            "Dockerizado",
        ],
    }
