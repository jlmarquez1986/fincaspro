"""
Regresión: las fechas se guardan en la base de datos como UTC "naive"
(sin zona horaria adjunta). Si la API las devuelve así tal cual, el
navegador de quien las reciba las interpreta como si YA estuvieran en su
hora local, desplazando la hora mostrada por su propio huso horario
(2 horas de más o de menos en España en verano, por ejemplo).

Estos tests comprueban que toda fecha que sale de la API lleva la zona
horaria explícita (sufijo "+00:00"), tal y como exige el estándar ISO 8601
para que cualquier cliente (navegador, móvil, otro backend) sepa
convertirla correctamente a la hora local de quien la esté viendo.
"""


def _tiene_zona_horaria_explicita(iso_string: str) -> bool:
    return iso_string.endswith("Z") or iso_string[-6] in ("+", "-")


def test_fecha_de_ticket_lleva_zona_horaria(client, auth_headers):
    res = client.post(
        "/api/tickets/",
        headers=auth_headers,
        data={"asunto": "Prueba de hora", "categoria": "otros"},
    )
    assert res.status_code == 201
    assert _tiene_zona_horaria_explicita(res.json()["creado_en"])
    assert _tiene_zona_horaria_explicita(res.json()["actualizado"])


def test_fecha_de_paquete_lleva_zona_horaria(client, auth_headers, db_session):
    from models import Vecino

    db_session.add(Vecino(nombre="Vecino", piso="1ºA", tipo="propietario"))
    db_session.commit()

    res = client.post(
        "/api/paqueteria/",
        headers=auth_headers,
        json={"vecino_id": 1, "remitente": "Amazon", "tamanio": "mediano"},
    )
    assert res.status_code == 201
    assert _tiene_zona_horaria_explicita(res.json()["recibido_en"])


def test_fecha_de_aviso_lleva_zona_horaria(client, auth_headers):
    res = client.post(
        "/api/avisos/",
        headers=auth_headers,
        json={"titulo": "Prueba", "contenido": "Contenido de prueba", "tipo": "info"},
    )
    assert res.status_code == 201
    assert _tiene_zona_horaria_explicita(res.json()["creado_en"])


def test_fecha_de_vecino_lleva_zona_horaria(client, auth_headers):
    res = client.post(
        "/api/vecinos/",
        headers=auth_headers,
        json={"nombre": "Vecino test", "piso": "2ºB"},
    )
    assert res.status_code == 201
    assert _tiene_zona_horaria_explicita(res.json()["creado_en"])
