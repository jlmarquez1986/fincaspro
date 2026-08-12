from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, field_validator


class UTCModel(BaseModel):
    """
    Los timestamps se guardan en la base de datos en UTC "naive" (sin
    zona horaria adjunta) — es lo correcto para no mezclar husos horarios
    en el almacenamiento. El problema es al devolverlos por la API: si el
    JSON no indica que ese valor es UTC, el navegador de quien lo reciba
    lo interpreta como si YA estuviera en su hora local, desplazando la
    hora mostrada por su propio huso horario (por ejemplo, 2h de más o de
    menos en España en horario de verano).

    Este validador marca cualquier datetime "naive" como UTC justo antes
    de serializarlo, para que la respuesta JSON siempre lleve el sufijo de
    zona horaria (+00:00). Con eso, el frontend puede convertirlo a la
    hora local de quien esté usando la app, sea cual sea su país.
    """

    @field_validator("*", mode="before")
    @classmethod
    def _mark_naive_datetimes_as_utc(cls, v):
        if isinstance(v, datetime) and v.tzinfo is None:
            return v.replace(tzinfo=UTC)
        return v


# ── Vecinos ──────────────────────────────────────────────
class VecinoBase(BaseModel):
    nombre: str
    email: str | None = None
    telefono: str | None = None
    piso: str
    tipo: str | None = "propietario"


class VecinoCreate(VecinoBase):
    pass


class VecinoPortalCreate(BaseModel):
    """Para que los vecinos activen su cuenta del portal"""

    nombre: str
    email: str
    password: str
    piso: str
    codigo_invitacion: str


class VecinoOut(UTCModel, VecinoBase):
    id: int
    portal_activo: str
    codigo_invitacion: str | None = None
    cargo: str | None = None  # <-- AÑADIR
    es_presidente: bool = False  # <-- AÑADIR
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)


class VecinoUpdate(BaseModel):
    nombre: str | None = None
    email: str | None = None
    telefono: str | None = None
    piso: str | None = None
    tipo: str | None = None
    portal_activo: str | None = None
    cargo: str | None = None  # <-- AÑADIR
    es_presidente: bool | None = None  # <-- AÑADIR


# ── Tickets ──────────────────────────────────────────────
class TicketBase(BaseModel):
    asunto: str
    descripcion: str | None = None
    categoria: str | None = "otros"
    prioridad: str | None = "normal"
    piso: str | None = None
    vecino_id: int | None = None
    asignado_a: str | None = None
    alcance: str | None = None


class TicketCreate(TicketBase):
    pass


class TicketUpdate(BaseModel):
    estado: str | None = None
    asignado_a: str | None = None
    prioridad: str | None = None
    alcance: str | None = None


class TicketOut(UTCModel, TicketBase):
    id: int
    estado: str
    foto_path: str | None = None
    creado_en: datetime
    actualizado: datetime
    model_config = ConfigDict(from_attributes=True)


class ComentarioCreate(BaseModel):
    autor: str | None = "Conserje"
    texto: str


class ComentarioOut(UTCModel, ComentarioCreate):
    id: int
    ticket_id: int
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)


# ── Paquetería ───────────────────────────────────────────
class PaqueteBase(BaseModel):
    remitente: str | None = None
    vecino_id: int
    tracking: str | None = None
    tamanio: str | None = "mediano"
    notificado: str | None = "no"


class PaqueteCreate(PaqueteBase):
    pass


class PaqueteOut(UTCModel, PaqueteBase):
    id: int
    estado: str
    recibido_en: datetime
    entregado_en: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


# ── Llaves ───────────────────────────────────────────────
class LlaveBase(BaseModel):
    nombre: str
    codigo: str
    descripcion: str | None = None


class LlaveCreate(LlaveBase):
    pass


class LlavePrestamo(BaseModel):
    prestada_a: str
    vecino_id: int | None = None


class LlaveOut(UTCModel, LlaveBase):
    id: int
    estado: str
    prestada_a: str | None = None
    desde: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


# ── Avisos ───────────────────────────────────────────────
class AvisoBase(BaseModel):
    titulo: str
    contenido: str
    tipo: str | None = "info"


class AvisoCreate(AvisoBase):
    pass


class AvisoOut(UTCModel, AvisoBase):
    id: int
    activo: str
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)


# ── Auth ─────────────────────────────────────────────────
class UsuarioCreate(BaseModel):
    nombre: str
    username: str
    email: str
    password: str
    rol: str | None = "conserje"


class UsuarioOut(BaseModel):
    id: int
    nombre: str
    username: str
    email: str
    rol: str
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)


class UsuarioUpdate(BaseModel):
    nombre: str | None = None
    username: str | None = None
    email: str | None = None
    password: str | None = None
    rol: str | None = None


class VecinoLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    usuario: dict


class VecinoToken(BaseModel):
    access_token: str
    token_type: str
    vecino: dict


# ── Email ────────────────────────────────────────────────
class EmailNotification(BaseModel):
    to: str
    subject: str
    body: str


# ─────────────────────────────────────────────────────────
# ── NUEVOS ESQUEMAS PARA LOS MÓDULOS ADICIONALES ──────
# ─────────────────────────────────────────────────────────


# ── Quejas y Mejoras ──────────────────────────────────
class QuejaMejoraBase(BaseModel):
    tipo: str  # 'queja' o 'mejora'
    categoria: str
    asunto: str
    descripcion: str | None = None
    prioridad: str | None = "media"


class QuejaMejoraCreate(QuejaMejoraBase):
    vecino_id: int | None = None


class QuejaMejoraUpdate(BaseModel):
    estado: str | None = None
    prioridad: str | None = None


class QuejaMejoraOut(UTCModel, QuejaMejoraBase):
    id: int
    estado: str
    vecino_id: int | None = None
    creado_por: int | None = None
    foto_path: str | None = None
    creado_en: datetime
    actualizado: datetime
    model_config = ConfigDict(from_attributes=True)


# ── Administrador ──────────────────────────────────────
class AdministradorBase(BaseModel):
    entidad: str  # 'comunidad' o 'mancomunidad'
    nombre: str
    telefono: str | None = None
    email: str | None = None
    direccion: str | None = None
    observaciones: str | None = None


class AdministradorCreate(AdministradorBase):
    pass


class AdministradorOut(UTCModel, AdministradorBase):
    id: int
    creado_en: datetime
    actualizado: datetime
    model_config = ConfigDict(from_attributes=True)


# ── Estado Cuenta ──────────────────────────────────────
class EstadoCuentaBase(BaseModel):
    entidad: str  # 'comunidad' o 'mancomunidad'
    mes: int  # 1-12
    anio: int
    saldo_inicial: float | None = 0.0
    ingresos: float | None = 0.0
    gastos: float | None = 0.0
    saldo_final: float | None = 0.0
    observaciones: str | None = None


class EstadoCuentaCreate(EstadoCuentaBase):
    pass


class EstadoCuentaOut(UTCModel, EstadoCuentaBase):
    id: int
    creado_en: datetime
    actualizado: datetime
    model_config = ConfigDict(from_attributes=True)


# ── Delegación Voto ────────────────────────────────────
class DelegacionVotoBase(BaseModel):
    vecino_delegante_id: int
    vecino_delegado_id: int
    dni_delegante: str | None = None
    asunto: str | None = None
    fecha_validez: datetime | None = None
    activa: bool | None = True


class DelegacionVotoCreate(DelegacionVotoBase):
    pass


class DelegacionVotoOut(UTCModel, DelegacionVotoBase):
    id: int
    fecha: datetime
    model_config = ConfigDict(from_attributes=True)


# ── Teléfono de Interés ───────────────────────────────
class TelefonoInteresBase(BaseModel):
    nombre: str
    telefono: str
    descripcion: str | None = None
    categoria: str | None = None  # seguros, ascensores, luz, agua, etc.


class TelefonoInteresCreate(TelefonoInteresBase):
    pass


class TelefonoInteresOut(UTCModel, TelefonoInteresBase):
    id: int
    creado_en: datetime
    actualizado: datetime
    model_config = ConfigDict(from_attributes=True)


# ── Carnet Piscina ─────────────────────────────────────
class CarnetPiscinaBase(BaseModel):
    vecino_id: int
    numero_carnet: str | None = None  # si no se proporciona, se genera automáticamente
    activo: bool | None = True


class CarnetPiscinaCreate(CarnetPiscinaBase):
    pass


class CarnetPiscinaOut(UTCModel, CarnetPiscinaBase):
    id: int
    fecha_expedicion: datetime
    model_config = ConfigDict(from_attributes=True)


# ── Invitación Piscina ─────────────────────────────────
class InvitacionPiscinaBase(BaseModel):
    vecino_id: int
    mes: int
    anio: int
    total_asignadas: int | None = 10
    usadas: int | None = 0


class InvitacionPiscinaOut(UTCModel, InvitacionPiscinaBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ── Registro Piscina ───────────────────────────────────
class RegistroPiscinaBase(BaseModel):
    vecino_id: int
    tipo: str  # 'propio' o 'invitacion'
    nombre_invitado: str | None = None


class RegistroPiscinaCreate(RegistroPiscinaBase):
    pass


class RegistroPiscinaOut(UTCModel, RegistroPiscinaBase):
    id: int
    fecha_hora: datetime
    registrado_por: int
    model_config = ConfigDict(from_attributes=True)
