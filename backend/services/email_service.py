"""
Servicio de notificaciones por email usando SMTP.
Compatible con cualquier proveedor SMTP gratuito:
  - Gmail (necesita contraseña de app)
  - Outlook/Hotmail
  - Mailgun (gratis hasta 5,000/mes)
  - SendGrid (gratis hasta 100/día)
  - Brevo (gratis hasta 300/día)
  - Cualquier servidor SMTP propio

Para desarrollo local sin cuenta real, usa MailHog (incluido en docker-compose).
"""

import os
from datetime import UTC, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from zoneinfo import ZoneInfo

import aiosmtplib

# Configuración desde variables de entorno (gratis, sin hardcodear)
SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
SMTP_PORT = int(os.getenv("SMTP_PORT", "1025"))  # 1025 = MailHog (dev), 587 = TLS
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SMTP_FROM = os.getenv("SMTP_FROM", "fincaspro@localhost")
SMTP_TLS = os.getenv("SMTP_TLS", "false").lower() == "true"

# Zona horaria para las fechas que se muestran DENTRO del texto de los
# emails. A diferencia de la web (donde el navegador convierte la hora
# automáticamente a la del dispositivo de quien la ve), un email es texto
# fijo: hay que decidir en qué huso horario se escribe. Por defecto se usa
# la de la comunidad (España); se puede cambiar por variable de entorno si
# la instalación está en otro país.
APP_TIMEZONE = os.getenv("APP_TIMEZONE", "Europe/Madrid")
COMMUNITY_NAME = os.getenv("COMMUNITY_NAME", "Comunidad El Roble")


def format_local(dt: datetime | None) -> str:
    """
    Formatea un datetime para mostrarlo en el texto de un email, convertido
    a APP_TIMEZONE. Los datetimes que vienen de la base de datos son UTC
    "naive" (sin zona horaria adjunta) — hay que decírselo explícitamente
    antes de convertir, o Python asumiría que ya están en hora local y no
    aplicaría ningún desplazamiento.
    """
    if dt is None:
        return "—"
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    local = dt.astimezone(ZoneInfo(APP_TIMEZONE))
    return local.strftime("%d/%m/%Y %H:%M")


async def send_email(
    to: str,
    subject: str,
    body: str,
    html_body: str | None = None,
    cc: list[str] | None = None,
) -> bool:
    """
    Envía un email de forma asíncrona.

    Args:
        to: Destinatario principal
        subject: Asunto
        body: Cuerpo en texto plano
        html_body: Cuerpo en HTML (opcional)
        cc: Lista de copias (opcional)

    Returns:
        True si se envió correctamente
    """
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = SMTP_FROM
        msg["To"] = to

        if cc:
            msg["Cc"] = ", ".join(cc)

        # Adjuntar versión texto plano
        msg.attach(MIMEText(body, "plain", "utf-8"))

        # Adjuntar versión HTML si existe
        if html_body:
            msg.attach(MIMEText(html_body, "html", "utf-8"))

        # Conectar y enviar
        await aiosmtplib.send(
            msg,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            username=SMTP_USER if SMTP_USER else None,
            password=SMTP_PASS if SMTP_PASS else None,
            start_tls=SMTP_TLS,
        )
        print(f"📧 Email enviado a {to}: {subject}")
        return True

    except Exception as e:
        print(f"❌ Error enviando email a {to}: {e}")
        return False


# ── Plantillas de notificación ───────────────────────────


async def notify_new_ticket(ticket, vecino_email: str) -> None:
    """Notifica a un vecino cuando se crea un ticket para él."""
    if not vecino_email:
        return

    subject = f"🔧 Nuevo ticket #{ticket.id}: {ticket.asunto}"

    body = f"""Hola,

Se ha registrado un nuevo ticket en FincasPro:

Asunto: {ticket.asunto}
Categoría: {ticket.categoria}
Prioridad: {ticket.prioridad}
Estado: {ticket.estado}
Piso/Zona: {ticket.piso or "No especificado"}

Descripción:
{ticket.descripcion or "Sin descripción"}

Puedes consultar el estado en tu portal de vecino.

Saludos,
FincasPro — {COMMUNITY_NAME}
"""

    priority_color = (
        "#ef4444"
        if ticket.prioridad == "urgente"
        else "#d97706"
        if ticket.prioridad == "media"
        else "#2563eb"
    )

    html = f"""
    <html>
    <body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;">
        <h2 style="color:#2563eb;">🔧 Nuevo Ticket #{ticket.id}</h2>

        <p><strong>Asunto:</strong> {ticket.asunto}</p>

        <p><strong>Categoría:</strong> {ticket.categoria}</p>

        <p>
            <strong>Prioridad:</strong>
            <span style="color:{priority_color};">
                {ticket.prioridad}
            </span>
        </p>

        <p><strong>Estado:</strong> {ticket.estado}</p>

        <p><strong>Piso/Zona:</strong> {ticket.piso or "No especificado"}</p>

        <div style="background:#f3f4f6;padding:12px;border-radius:8px;margin:12px 0;">
            <p style="margin:0;">
                <strong>Descripción:</strong><br/>
                {ticket.descripcion or "Sin descripción"}
            </p>
        </div>

        <p style="color:#6b7280;font-size:12px;">
            FincasPro — {COMMUNITY_NAME}
        </p>
    </body>
    </html>
    """

    await send_email(vecino_email, subject, body, html)


async def notify_ticket_status_change(ticket, vecino_email: str, old_status: str) -> None:
    """Notifica cuando cambia el estado de un ticket."""
    if not vecino_email:
        return

    subject = f"📋 Ticket #{ticket.id} actualizado: {ticket.estado}"
    body = f"""Hola,

El estado de tu ticket ha cambiado:

Asunto: {ticket.asunto}
Estado anterior: {old_status}
Estado actual: {ticket.estado}

Puedes consultar los detalles en tu portal de vecino.

Saludos,
FincasPro
"""
    await send_email(vecino_email, subject, body)


async def notify_new_package(paquete, vecino_email: str, vecino_nombre: str) -> None:
    """Notifica a un vecino cuando llega un paquete."""
    if not vecino_email:
        return

    subject = f"📦 Paquete recibido de {paquete.remitente or 'remitente desconocido'}"
    body = f"""Hola {vecino_nombre},

Hemos recibido un paquete para ti:

Remitente: {paquete.remitente or "No especificado"}
Tamaño: {paquete.tamanio}
Fecha de recepción: {format_local(paquete.recibido_en)}

Puedes pasar a recogerlo por conserjería.

Saludos,
FincasPro — {COMMUNITY_NAME}
"""
    html = f"""
    <html><body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;">
    <h2 style="color:#2563eb;">📦 Paquete Recibido</h2>
    <p>Hola <strong>{vecino_nombre}</strong>,</p>
    <p>Hemos recibido un paquete para ti:</p>
    <div style="background:#f3f4f6;padding:12px;border-radius:8px;margin:12px 0;">
        <p><strong>Remitente:</strong> {paquete.remitente or "No especificado"}</p>
        <p><strong>Tamaño:</strong> {paquete.tamanio}</p>
        <p><strong>Fecha:</strong> {format_local(paquete.recibido_en)}</p>
    </div>
    <p>Puedes pasar a recogerlo por conserjería.</p>
    <p style="color:#6b7280;font-size:12px;">FincasPro — {COMMUNITY_NAME}</p>
    </body></html>
    """
    await send_email(vecino_email, subject, body, html)


async def notify_new_aviso(aviso, vecino_email: str) -> None:
    """Notifica de un nuevo aviso/comunicado."""
    if not vecino_email:
        return

    subject = f"📢 {aviso.titulo}"

    body = f"""Hola,

Nuevo aviso publicado en el tablón:

{aviso.titulo}

{aviso.contenido}

Saludos,
FincasPro — {COMMUNITY_NAME}
"""

    aviso_color = (
        "#ef4444" if aviso.tipo == "urgente" else "#d97706" if aviso.tipo == "aviso" else "#2563eb"
    )

    html = f"""
    <html>
    <body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;">

        <h2 style="color:{aviso_color};">
            📢 {aviso.titulo}
        </h2>

        <div style="background:#f3f4f6;padding:12px;border-radius:8px;margin:12px 0;">
            <p style="margin:0;white-space:pre-wrap;">
                {aviso.contenido}
            </p>
        </div>

        <p style="color:#6b7280;font-size:12px;">
            FincasPro — {COMMUNITY_NAME}
        </p>

    </body>
    </html>
    """

    await send_email(vecino_email, subject, body, html)


async def notify_key_return_reminder(llave, vecino_email: str) -> None:
    """Recordatorio para devolver una llave."""
    if not vecino_email:
        return

    subject = f"🔑 Recordatorio: devolver llave {llave.nombre}"
    body = f"""Hola,

Te recordamos que tienes prestada la llave:

{llave.nombre} ({llave.codigo})
Prestada el: {format_local(llave.desde)}

Por favor, devuélvela a conserjería lo antes posible.

Saludos,
FincasPro
"""
    await send_email(vecino_email, subject, body)
