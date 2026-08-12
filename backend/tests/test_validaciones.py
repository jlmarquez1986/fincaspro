"""
Tests de validaciones Pydantic (HTTP 422).
Verifica que la API rechace datos inválidos con mensajes claros.
"""


def test_crear_vecino_sin_nombre_devuelve_422(client, auth_headers):
    res = client.post(
        "/api/vecinos/",
        headers=auth_headers,
        json={"piso": "1ºA"},  # falta nombre
    )
    assert res.status_code == 422


def test_crear_vecino_sin_piso_devuelve_422(client, auth_headers):
    res = client.post(
        "/api/vecinos/",
        headers=auth_headers,
        json={"nombre": "Sin piso"},
    )
    assert res.status_code == 422


def test_crear_ticket_sin_asunto_devuelve_422(client, auth_headers):
    res = client.post(
        "/api/tickets/",
        headers=auth_headers,
        data={"categoria": "otros"},  # falta asunto
    )
    assert res.status_code == 422


def test_crear_usuario_sin_email_devuelve_422(client, auth_headers):
    res = client.post(
        "/api/usuarios/",
        headers=auth_headers,
        json={"nombre": "X", "username": "x", "password": "12345678"},
    )
    assert res.status_code == 422


def test_crear_paquete_sin_vecino_id_devuelve_422(client, auth_headers):
    res = client.post(
        "/api/paqueteria/",
        headers=auth_headers,
        json={"remitente": "Amazon"},
    )
    assert res.status_code == 422


def test_crear_aviso_sin_titulo_devuelve_422(client, auth_headers):
    res = client.post(
        "/api/avisos/",
        headers=auth_headers,
        json={"contenido": "Solo contenido"},
    )
    assert res.status_code == 422


def test_crear_estado_cuenta_sin_entidad_devuelve_422(client, auth_headers):
    res = client.post(
        "/api/estados-cuenta/",
        headers=auth_headers,
        json={"mes": 1, "anio": 2026},
    )
    assert res.status_code == 422


def test_crear_llave_sin_codigo_devuelve_422(client, auth_headers):
    res = client.post(
        "/api/llaves/",
        headers=auth_headers,
        json={"nombre": "Sala de máquinas"},
    )
    assert res.status_code == 422
