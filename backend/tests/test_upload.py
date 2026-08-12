"""
Tests de upload de imágenes (multipart/form-data).
Verifica que se puedan adjuntar fotos a tickets y quejas.
"""

import io


def _imagen_fake() -> io.BytesIO:
    """Genera un PNG mínimo válido de 1×1 píxel (43 bytes)."""
    # PNG mínimo 1x1 píxel — representado como lista de bytes hex
    # para evitar problemas de encoding con caracteres no-ASCII.
    data = bytes(
        [
            0x89,
            0x50,
            0x4E,
            0x47,
            0x0D,
            0x0A,
            0x1A,
            0x0A,
            0x00,
            0x00,
            0x00,
            0x0D,
            0x49,
            0x48,
            0x44,
            0x52,
            0x00,
            0x00,
            0x00,
            0x01,
            0x00,
            0x00,
            0x00,
            0x01,
            0x08,
            0x02,
            0x00,
            0x00,
            0x00,
            0x90,
            0x77,
            0x53,
            0xDE,
            0x00,
            0x00,
            0x00,
            0x0C,
            0x49,
            0x44,
            0x41,
            0x54,
            0x08,
            0xD7,
            0x63,
            0xF8,
            0xCF,
            0xC0,
            0x00,
            0x00,
            0x00,
            0x03,
            0x00,
            0x01,
            0x00,
            0x05,
            0xFE,
            0xD8,
            0x00,
            0x00,
            0x00,
            0x00,
            0x49,
            0x45,
            0x4E,
            0x44,
            0xAE,
            0x42,
            0x60,
            0x82,
        ]
    )
    return io.BytesIO(data)


def test_crear_ticket_con_foto(client, auth_headers):
    img = _imagen_fake()
    res = client.post(
        "/api/tickets/",
        headers=auth_headers,
        data={
            "asunto": "Ticket con imagen",
            "categoria": "otros",
            "prioridad": "normal",
        },
        files={"foto": ("test.png", img, "image/png")},
    )
    assert res.status_code == 201
    body = res.json()
    assert body["asunto"] == "Ticket con imagen"
    assert body["foto_path"] is not None
    assert "/uploads/tickets/" in body["foto_path"]


def test_crear_queja_con_foto(client, auth_headers):
    img = _imagen_fake()
    res = client.post(
        "/api/quejas-mejoras/",
        headers=auth_headers,
        data={
            "tipo": "queja",
            "categoria": "limpieza",
            "asunto": "Suciedad con foto",
            "prioridad": "media",
        },
        files={"foto": ("suciedad.png", img, "image/png")},
    )
    assert res.status_code == 201
    body = res.json()
    assert body["foto_path"] is not None
