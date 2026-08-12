"""Tests CRUD de quejas y mejoras."""

from models import QuejaMejora


def test_listar_quejas_mejoras(client, auth_headers, db_session):
    db_session.add(
        QuejaMejora(tipo="queja", categoria="limpieza", asunto="Suciedad", estado="pendiente")
    )
    db_session.commit()

    res = client.get("/api/quejas-mejoras/", headers=auth_headers)
    assert res.status_code == 200
    assert len(res.json()) >= 1


def test_listar_quejas_filtradas(client, auth_headers, db_session):
    db_session.add(QuejaMejora(tipo="queja", categoria="limpieza", asunto="A", estado="pendiente"))
    db_session.add(
        QuejaMejora(tipo="mejora", categoria="jardineria", asunto="B", estado="resuelto")
    )
    db_session.commit()

    res = client.get("/api/quejas-mejoras/?tipo=mejora", headers=auth_headers)
    assert res.status_code == 200
    assert all(q["tipo"] == "mejora" for q in res.json())


def test_crear_queja(client, auth_headers):
    res = client.post(
        "/api/quejas-mejoras/",
        headers=auth_headers,
        data={
            "tipo": "queja",
            "categoria": "ruido",
            "asunto": "Ruido nocturno",
            "descripcion": "El vecino del 4º hace fiesta",
            "prioridad": "alta",
        },
    )
    assert res.status_code == 201
    assert res.json()["asunto"] == "Ruido nocturno"
    assert res.json()["estado"] == "pendiente"


def test_actualizar_queja(client, auth_headers, db_session):
    q = QuejaMejora(tipo="queja", categoria="ascensor", asunto="Parado", estado="pendiente")
    db_session.add(q)
    db_session.commit()
    db_session.refresh(q)

    res = client.patch(
        f"/api/quejas-mejoras/{q.id}",
        headers=auth_headers,
        json={"estado": "resuelto", "prioridad": "baja"},
    )
    assert res.status_code == 200
    assert res.json()["estado"] == "resuelto"
    assert res.json()["prioridad"] == "baja"


def test_eliminar_queja_como_admin(client, auth_headers, db_session):
    q = QuejaMejora(tipo="queja", categoria="otros", asunto="Borrar", estado="pendiente")
    db_session.add(q)
    db_session.commit()
    db_session.refresh(q)

    res = client.delete(f"/api/quejas-mejoras/{q.id}", headers=auth_headers)
    assert res.status_code == 204


def test_eliminar_queja_como_conserje_devuelve_403(client, conserje_headers, db_session):
    q = QuejaMejora(tipo="queja", categoria="otros", asunto="Protegida", estado="pendiente")
    db_session.add(q)
    db_session.commit()
    db_session.refresh(q)

    res = client.delete(f"/api/quejas-mejoras/{q.id}", headers=conserje_headers)
    assert res.status_code == 403
