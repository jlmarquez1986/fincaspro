"""
Script de carga de datos de prueba para FincasPro.
Ejecutar UNA sola vez: python seed.py
"""

import secrets
import string
from datetime import timedelta
from typing import Any

from database import Base, SessionLocal, engine, utcnow
from models import (
    Administrador,
    Aviso,
    CarnetPiscina,
    Configuracion,
    DelegacionVoto,
    EstadoCuenta,
    InvitacionPiscina,
    Llave,
    Paquete,
    QuejaMejora,
    RegistroPiscina,
    TelefonoInteres,
    Ticket,
    Usuario,
    Vecino,
)
from security import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

print("🌱 Cargando datos de prueba...")

# ── Usuarios ──────────────────────────────────────────────
users = [
    Usuario(
        nombre="Admin Sistema",
        username="admin",
        email="admin@fincaspro.com",
        password=hash_password("admin123"),
        rol="admin",
    ),
    Usuario(
        nombre="Carlos Jiménez",
        username="conserje",
        email="carlos@fincaspro.com",
        password=hash_password("conserje123"),
        rol="conserje",
    ),
    Usuario(
        nombre="Socorrista Piscina",
        username="socorrista",
        email="socorrista@fincaspro.com",
        password=hash_password("socorrista123"),
        rol="socorrista",
    ),
]
db.add_all(users)
db.commit()


# ── Vecinos ──────────────────────────────────────────────
def generar_codigo():
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(6))


vecinos_data: list[dict[str, Any]] = [
    {
        "nombre": "María García",
        "email": "maria@email.com",
        "telefono": "612345678",
        "piso": "2D",
        "tipo": "propietario",
        "cargo": "presidente",
        "es_presidente": True,
    },
    {
        "nombre": "Pedro Ruiz",
        "email": "pedro@email.com",
        "telefono": "654987321",
        "piso": "5A",
        "tipo": "inquilino",
        "cargo": None,
        "es_presidente": False,
    },
    {
        "nombre": "Ana Martínez",
        "email": "ana@email.com",
        "telefono": "699111222",
        "piso": "1C",
        "tipo": "propietario",
        "cargo": "vicepresidente",
        "es_presidente": False,
    },
    {
        "nombre": "Luis Fernández",
        "email": "luis@email.com",
        "telefono": "677444555",
        "piso": "4B",
        "tipo": "propietario",
        "cargo": "secretario",
        "es_presidente": False,
    },
    {
        "nombre": "Elena Soler",
        "email": "elena@email.com",
        "telefono": "600333999",
        "piso": "6C",
        "tipo": "inquilino",
        "cargo": None,
        "es_presidente": False,
    },
    {
        "nombre": "Javier Torres",
        "email": "javier@email.com",
        "telefono": "622888777",
        "piso": "3A",
        "tipo": "propietario",
        "cargo": "tesorero",
        "es_presidente": False,
    },
]
vecinos = []
for vd in vecinos_data:
    codigo = generar_codigo()
    while db.query(Vecino).filter(Vecino.codigo_invitacion == codigo).first():
        codigo = generar_codigo()
    vecino = Vecino(
        nombre=vd["nombre"],
        email=vd["email"],
        telefono=vd["telefono"],
        piso=vd["piso"],
        tipo=vd["tipo"],
        password=(
            hash_password("vecino123")
            if vd["email"] in ["maria@email.com", "pedro@email.com"]
            else None
        ),
        portal_activo="true" if vd["email"] in ["maria@email.com", "pedro@email.com"] else "false",
        codigo_invitacion=codigo,
        cargo=vd["cargo"],
        es_presidente=vd["es_presidente"],
    )
    vecinos.append(vecino)
db.add_all(vecinos)
db.commit()

# Mapas para referencias
v_map = {v.piso: v for v in vecinos}

# ── Carnets de Piscina ──────────────────────────────────
carnets = [
    CarnetPiscina(vecino_id=vecinos[0].id, numero_carnet="P-A1B2", activo=True),
    CarnetPiscina(vecino_id=vecinos[1].id, numero_carnet="P-C3D4", activo=True),
    CarnetPiscina(vecino_id=vecinos[2].id, numero_carnet="P-E5F6", activo=True),
]
db.add_all(carnets)
db.commit()

# ── Invitaciones Piscina (mes actual) ──────────────────
hoy = utcnow()
for v in vecinos[:3]:
    inv = InvitacionPiscina(
        vecino_id=v.id, mes=hoy.month, anio=hoy.year, total_asignadas=10, usadas=0
    )
    db.add(inv)
db.commit()

# ── Registros Piscina ──────────────────────────────────
registros = [
    RegistroPiscina(vecino_id=vecinos[0].id, tipo="propio", registrado_por=users[2].id),
    RegistroPiscina(
        vecino_id=vecinos[1].id,
        tipo="invitacion",
        nombre_invitado="Amigo Pedro",
        registrado_por=users[2].id,
    ),
]
db.add_all(registros)
db.commit()

# ── Configuración ──────────────────────────────────────
configs = [
    Configuracion(
        clave="invitaciones_mensuales",
        valor="10",
        descripcion="Número de invitaciones por vecino al mes",
    ),
]
db.add_all(configs)
db.commit()

# ── Tickets ──────────────────────────────────────────────
tickets = [
    Ticket(
        asunto="Fuga de agua en el baño principal",
        descripcion="Hay una fuga importante bajo el lavabo.",
        categoria="fontaneria",
        prioridad="urgente",
        estado="en_proceso",
        piso="3B",
        vecino_id=vecinos[0].id,
    ),
    Ticket(
        asunto="Bombilla del portal fundida",
        descripcion="La luz de la entrada principal no funciona.",
        categoria="electricidad",
        prioridad="media",
        estado="en_proceso",
        piso="Comunal",
    ),
    Ticket(
        asunto="Ruido extraño en el ascensor",
        descripcion="Se escucha un chirrido al subir al 4º.",
        categoria="ascensor",
        prioridad="normal",
        estado="pendiente",
        piso="Comunal",
    ),
    Ticket(
        asunto="Grifo de la cocina gotea",
        descripcion="El grifo de la cocina gotea constantemente.",
        categoria="fontaneria",
        prioridad="baja",
        estado="resuelto",
        piso="1A",
        vecino_id=vecinos[2].id,
    ),
    Ticket(
        asunto="Puerta del garaje no cierra bien",
        descripcion="La barrera se queda a medio bajar.",
        categoria="cerrajeria",
        prioridad="media",
        estado="en_proceso",
        piso="Garaje",
    ),
    Ticket(
        asunto="Interruptor escalera 2ª planta roto",
        descripcion="No enciende la luz en ese tramo.",
        categoria="electricidad",
        prioridad="normal",
        estado="resuelto",
        piso="Comunal",
    ),
    Ticket(
        asunto="Humedad en techo del sótano",
        descripcion="Mancha de humedad creciente.",
        categoria="fontaneria",
        prioridad="media",
        estado="pendiente",
        piso="Sótano",
    ),
]
db.add_all(tickets)
db.commit()

# ── Paquetes ─────────────────────────────────────────────
pkgs = [
    Paquete(
        remitente="Amazon",
        vecino_id=vecinos[0].id,
        tamanio="mediano",
        estado="pendiente",
        notificado="si",
        recibido_en=utcnow() - timedelta(hours=2),
    ),
    Paquete(
        remitente="Correos",
        vecino_id=vecinos[1].id,
        tamanio="sobre",
        estado="pendiente",
        notificado="no",
        recibido_en=utcnow() - timedelta(days=1, hours=3),
    ),
    Paquete(
        remitente="Seur",
        vecino_id=vecinos[2].id,
        tamanio="grande",
        estado="pendiente",
        notificado="si",
        recibido_en=utcnow() - timedelta(days=1, hours=8),
    ),
    Paquete(
        remitente="Amazon",
        vecino_id=vecinos[3].id,
        tamanio="pequeno",
        estado="entregado",
        notificado="si",
        recibido_en=utcnow() - timedelta(days=2),
        entregado_en=utcnow() - timedelta(days=1),
    ),
]
db.add_all(pkgs)
db.commit()

# ── Llaves ────────────────────────────────────────────────
llaves = [
    Llave(
        nombre="Portal principal",
        codigo="P-1",
        descripcion="Llave maestra portal",
        estado="disponible",
    ),
    Llave(
        nombre="Portal trasero",
        codigo="P-2",
        descripcion="Entrada trasera jardín",
        estado="disponible",
    ),
    Llave(
        nombre="Trastero 12",
        codigo="T-12",
        descripcion="Trastero planta sótano",
        estado="prestada",
        prestada_a="Luis Fernández (4B)",
        vecino_id=vecinos[3].id,
        desde=utcnow() - timedelta(days=2),
    ),
    Llave(
        nombre="Trastero 7", codigo="T-7", descripcion="Trastero planta sótano", estado="disponible"
    ),
    Llave(
        nombre="Local comercial B",
        codigo="LC-B",
        descripcion="Local en planta baja",
        estado="prestada",
        prestada_a="Elena Soler (6C)",
        vecino_id=vecinos[4].id,
        desde=utcnow() - timedelta(hours=3),
    ),
    Llave(
        nombre="Garaje acceso",
        codigo="G-1",
        descripcion="Acceso peatonal garaje",
        estado="disponible",
    ),
    Llave(
        nombre="Garaje barrera",
        codigo="G-2",
        descripcion="Control barrera garaje",
        estado="disponible",
    ),
    Llave(nombre="Azotea", codigo="AZ", descripcion="Acceso a la azotea", estado="disponible"),
]
db.add_all(llaves)
db.commit()

# ── Avisos ────────────────────────────────────────────────
avisos = [
    Aviso(
        titulo="Corte de agua — 5 junio",
        contenido=(
            "Corte de suministro de agua el miércoles 5 de junio"
            "de 9:00 a 14:00 h por obras en la red municipal."
        ),
        tipo="aviso",
    ),
    Aviso(
        titulo="Junta de propietarios — 15 junio",
        contenido="Se convoca junta ordinaria el 15 de junio a las 20:00 h en el salón de actos.",
        tipo="info",
    ),
    Aviso(
        titulo="Alerta de seguridad en parking",
        contenido=(
            "Se han detectado intentos de acceso no autorizado.No abrir la barrera a desconocidos."
        ),
        tipo="urgente",
    ),
]
db.add_all(avisos)
db.commit()

# ── Quejas y Mejoras ──────────────────────────────────────
quejas_mejoras = [
    QuejaMejora(
        tipo="queja",
        categoria="ascensores",
        asunto="Ascensor tarda mucho en cerrar",
        descripcion="El ascensor tarda más de 10 segundos en cerrar la puerta.",
        estado="pendiente",
        prioridad="media",
        vecino_id=vecinos[0].id,
        creado_por=users[0].id,
    ),
    QuejaMejora(
        tipo="mejora",
        categoria="jardineria",
        asunto="Instalar riego automático",
        descripcion="Propuesta para instalar sistema de riego automático en las zonas verdes.",
        estado="en_proceso",
        prioridad="baja",
        vecino_id=vecinos[1].id,
        creado_por=users[1].id,
    ),
    QuejaMejora(
        tipo="queja",
        categoria="limpieza",
        asunto="Suelos del portal sucios",
        descripcion="La limpieza del portal no se realiza con la frecuencia adecuada.",
        estado="resuelto",
        prioridad="alta",
        vecino_id=vecinos[2].id,
        creado_por=users[0].id,
    ),
    QuejaMejora(
        tipo="mejora",
        categoria="seguridad",
        asunto="Cámaras de seguridad",
        descripcion="Sugerencia de instalar cámaras en zonas comunes para mayor seguridad.",
        estado="pendiente",
        prioridad="media",
        vecino_id=None,
        creado_por=users[0].id,
    ),
]
db.add_all(quejas_mejoras)
db.commit()

# ── Administradores ──────────────────────────────────────
admins = [
    Administrador(
        entidad="comunidad",
        nombre="Gescom SL",
        telefono="911234567",
        email="info@gescom.com",
        direccion="Calle Mayor 1, 28001 Madrid",
        observaciones="Administrador de la comunidad",
    ),
    Administrador(
        entidad="mancomunidad",
        nombre="Mancomunidad Integral",
        telefono="912345678",
        email="info@mancomunidad.es",
        direccion="Avenida de la Mancomunidad 22, 28935 Móstoles",
        observaciones="Mancomunidad de servicios",
    ),
]
db.add_all(admins)
db.commit()

# ── Estados de Cuenta ──────────────────────────────────
estados = [
    EstadoCuenta(
        entidad="comunidad",
        mes=6,
        anio=2026,
        saldo_inicial=15000,
        ingresos=3000,
        gastos=2500,
        saldo_final=15500,
        observaciones="Mes de junio, obras de pintura",
    ),
    EstadoCuenta(
        entidad="comunidad",
        mes=5,
        anio=2026,
        saldo_inicial=12000,
        ingresos=3500,
        gastos=500,
        saldo_final=15000,
        observaciones="Mayo, cuotas al día",
    ),
    EstadoCuenta(
        entidad="mancomunidad",
        mes=6,
        anio=2026,
        saldo_inicial=8000,
        ingresos=2000,
        gastos=1800,
        saldo_final=8200,
        observaciones="Gastos de mantenimiento",
    ),
]
db.add_all(estados)
db.commit()

# ── Delegaciones de Voto ──────────────────────────────────
delegaciones = [
    DelegacionVoto(
        vecino_delegante_id=vecinos[0].id,
        vecino_delegado_id=vecinos[1].id,
        dni_delegante="12345678A",
        asunto="Junta extraordinaria 15/06",
        activa=True,
    ),
    DelegacionVoto(
        vecino_delegante_id=vecinos[2].id,
        vecino_delegado_id=vecinos[3].id,
        dni_delegante="87654321B",
        asunto="Junta ordinaria anual",
        activa=True,
    ),
    DelegacionVoto(
        vecino_delegante_id=vecinos[4].id,
        vecino_delegado_id=vecinos[5].id,
        dni_delegante="11223344C",
        asunto="Delegación temporal por viaje",
        activa=False,
    ),
]
db.add_all(delegaciones)
db.commit()

# ── Teléfonos de Interés ──────────────────────────────────
telefonos = [
    TelefonoInteres(
        nombre="Seguro Hogar Mapfre",
        telefono="900123456",
        descripcion="Seguro de la comunidad",
        categoria="Seguros",
    ),
    TelefonoInteres(
        nombre="Ascensores Schindler",
        telefono="911234567",
        descripcion="Mantenimiento de ascensores",
        categoria="Ascensores",
    ),
    TelefonoInteres(
        nombre="Iberdrola",
        telefono="900123456",
        descripcion="Suministro eléctrico",
        categoria="Luz",
    ),
    TelefonoInteres(
        nombre="Canal de Isabel II",
        telefono="901123456",
        descripcion="Suministro de agua",
        categoria="Agua",
    ),
    TelefonoInteres(
        nombre="Jardinería Verde",
        telefono="912345678",
        descripcion="Mantenimiento jardines",
        categoria="Jardinería",
    ),
    TelefonoInteres(
        nombre="Piscinas Real",
        telefono="913456789",
        descripcion="Mantenimiento piscina",
        categoria="Piscina",
    ),
]
db.add_all(telefonos)
db.commit()

db.close()
print("✅ Datos cargados correctamente.")
print("   👤 Admin: admin / admin123")
print("   👤 Conserje: conserje / conserje123")
print("   👤 Socorrista: socorrista / socorrista123")
print("   🏠 Vecinos con portal: maria@email.com / vecino123")
print("   🏠 Vecinos con portal: pedro@email.com / vecino123")
