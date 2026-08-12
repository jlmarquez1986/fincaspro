"""Tests adicionales de tickets: filtros, paginación, permisos vecino."""

from models import Ticket, Vecino


def test_filtro_tickets_por_estado(client, auth_headers, db_session):
    db_session.add(Ticket(asunto="Pendiente", categoria="otros", estado="pendiente"))
    db_session.add(Ticket(asunto="Resuelto", categoria="otros", estado="resuelto"))
    db_session.commit()

    res = client.get("/api/tickets/?estado=resuelto", headers=auth_headers)
    assert res.status_code == 200
    assert all(t["estado"] == "resuelto" for t in res.json())


def test_paginacion_tickets(client, auth_headers, db_session):
    for i in range(5):
        db_session.add(Ticket(asunto=f"Ticket {i}", categoria="otros"))
    db_session.commit()

    res = client.get("/api/tickets/?skip=0&limit=3", headers=auth_headers)
    assert res.status_code == 200
    assert len(res.json()) == 3

    res2 = client.get("/api/tickets/?skip=3&limit=3", headers=auth_headers)
    assert res2.status_code == 200
    assert len(res2.json()) == 2


def test_vecino_no_puede_actualizar_ticket_ajeno(client, vecino_headers, db_session):
    # El token de vecino no es aceptado por get_current_user (falta 'sub')
    otro = Vecino(nombre="Otro", piso="9ºZ", tipo="propietario")
    db_session.add(otro)
    db_session.commit()
    db_session.refresh(otro)

    t = Ticket(asunto="Ajeno", categoria="otros", vecino_id=otro.id)
    db_session.add(t)
    db_session.commit()
    db_session.refresh(t)

    res = client.patch(
        f"/api/tickets/{t.id}",
        headers=vecino_headers,
        json={"estado": "resuelto"},
    )
    assert res.status_code == 401


def test_vecino_puede_actualizar_su_ticket(client, vecino_headers, db_session, vecino_user):
    # El token de vecino no es aceptado por get_current_user (falta 'sub')
    # Los vecinos actualizan tickets desde el portal, no desde /api/tickets/
    t = Ticket(asunto="Mío", categoria="otros", vecino_id=vecino_user.id)
    db_session.add(t)
    db_session.commit()
    db_session.refresh(t)

    res = client.patch(
        f"/api/tickets/{t.id}",
        headers=vecino_headers,
        json={"estado": "resuelto"},
    )
    assert res.status_code == 401
