"""Tests de comentarios en tickets."""

from models import Ticket, Vecino


def test_agregar_comentario_a_ticket(client, auth_headers, db_session):
    t = Ticket(asunto="Con comentarios", categoria="otros")
    db_session.add(t)
    db_session.commit()
    db_session.refresh(t)

    res = client.post(
        f"/api/tickets/{t.id}/comentarios",
        headers=auth_headers,
        json={"texto": "Revisado, llamar al fontanero"},
    )
    assert res.status_code == 201
    assert res.json()["texto"] == "Revisado, llamar al fontanero"
    assert res.json()["autor"] == "Admin de Prueba"


def test_comentar_ticket_inexistente_devuelve_404(client, auth_headers):
    res = client.post(
        "/api/tickets/99999/comentarios",
        headers=auth_headers,
        json={"texto": "Nadie me lee"},
    )
    assert res.status_code == 404


def test_vecino_comenta_su_ticket(client, vecino_headers, db_session, vecino_user):
    # El endpoint /api/tickets/{id}/comentarios usa get_current_user, no get_current_vecino
    # Un vecino no puede comentar ahí directamente (401 porque su token no tiene 'sub')
    t = Ticket(asunto="Mi ticket", categoria="otros", vecino_id=vecino_user.id)
    db_session.add(t)
    db_session.commit()
    db_session.refresh(t)

    res = client.post(
        f"/api/tickets/{t.id}/comentarios",
        headers=vecino_headers,
        json={"texto": "¿Hay novedades?"},
    )
    assert res.status_code == 401


def test_vecino_no_comenta_ticket_ajeno(client, vecino_headers, db_session):
    otro = Vecino(nombre="Otro", piso="9ºZ", tipo="propietario")
    db_session.add(otro)
    db_session.commit()
    db_session.refresh(otro)

    t = Ticket(asunto="Ajeno", categoria="otros", vecino_id=otro.id)
    db_session.add(t)
    db_session.commit()
    db_session.refresh(t)

    res = client.post(
        f"/api/tickets/{t.id}/comentarios",
        headers=vecino_headers,
        json={"texto": "Intruso"},
    )
    # 401 porque el token de vecino no tiene 'sub' (username)
    assert res.status_code == 401
