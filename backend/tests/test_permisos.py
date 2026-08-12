"""
Tests de autorización por rol.
Verifica que cada rol solo pueda hacer lo que le corresponde.
"""

from models import Ticket, Vecino


def test_conserje_no_puede_crear_usuario(client, conserje_headers):
    res = client.post(
        "/api/usuarios/",
        headers=conserje_headers,
        json={
            "nombre": "Hackeo",
            "username": "hacker",
            "email": "h@ck.com",
            "password": "12345678",
        },
    )
    assert res.status_code == 403


def test_conserje_no_puede_eliminar_vecino(client, conserje_headers, db_session):
    v = Vecino(nombre="Protegido", piso="8ºA", tipo="propietario")
    db_session.add(v)
    db_session.commit()
    db_session.refresh(v)

    res = client.delete(f"/api/vecinos/{v.id}", headers=conserje_headers)
    assert res.status_code == 403


def test_conserje_puede_crear_ticket(client, conserje_headers):
    res = client.post(
        "/api/tickets/",
        headers=conserje_headers,
        data={"asunto": "Ticket conserje", "categoria": "limpieza"},
    )
    assert res.status_code == 201


def test_vecino_no_puede_listar_usuarios(client, vecino_headers):
    res = client.get("/api/usuarios/", headers=vecino_headers)
    # El token de vecino no tiene 'sub' (username), get_current_user rechaza con 401
    assert res.status_code == 401


def test_vecino_no_puede_ver_tickets_de_otros(client, vecino_headers, db_session, auth_headers):
    # Admin crea un ticket para otro vecino
    otro = Vecino(nombre="Otro", piso="9ºZ", tipo="propietario")
    db_session.add(otro)
    db_session.commit()
    db_session.refresh(otro)

    ticket = Ticket(asunto="Privado", categoria="otros", vecino_id=otro.id)
    db_session.add(ticket)
    db_session.commit()

    # El vecino usa el endpoint del portal para ver SUS tickets
    res = client.get("/api/portal/mis-tickets", headers=vecino_headers)
    assert res.status_code == 200
    ids = [t["id"] for t in res.json()]
    assert ticket.id not in ids


def test_vecino_puede_ver_sus_tickets(client, vecino_headers, db_session, vecino_user):
    ticket = Ticket(asunto="Mío", categoria="otros", vecino_id=vecino_user.id)
    db_session.add(ticket)
    db_session.commit()

    res = client.get("/api/portal/mis-tickets", headers=vecino_headers)
    assert res.status_code == 200
    ids = [t["id"] for t in res.json()]
    assert ticket.id in ids


def test_admin_puede_eliminar_ticket(client, auth_headers):
    creado = client.post(
        "/api/tickets/",
        headers=auth_headers,
        data={"asunto": "Para borrar", "categoria": "otros"},
    ).json()

    res = client.delete(f"/api/tickets/{creado['id']}", headers=auth_headers)
    assert res.status_code == 204


def test_sin_token_en_endpoint_protegido(client):
    res = client.get("/api/usuarios/")
    assert res.status_code == 401
