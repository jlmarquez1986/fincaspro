"""Tests CRUD completo de vecinos (admin) y registro portal."""

from models import Vecino


def test_listar_vecinos(client, auth_headers):
    res = client.get("/api/vecinos/", headers=auth_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_obtener_vecino_por_id(client, auth_headers, db_session):
    v = Vecino(nombre="Juan", piso="1ºA", tipo="propietario")
    db_session.add(v)
    db_session.commit()
    db_session.refresh(v)

    res = client.get(f"/api/vecinos/{v.id}", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["nombre"] == "Juan"
    assert res.json()["piso"] == "1ºA"


def test_obtener_vecino_inexistente_devuelve_404(client, auth_headers):
    res = client.get("/api/vecinos/99999", headers=auth_headers)
    assert res.status_code == 404


def test_crear_vecino_como_admin_genera_codigo_invitacion(client, auth_headers):
    res = client.post(
        "/api/vecinos/",
        headers=auth_headers,
        json={"nombre": "María López", "piso": "4ºC", "tipo": "inquilino"},
    )
    assert res.status_code == 201
    body = res.json()
    assert body["nombre"] == "María López"
    assert body["codigo_invitacion"] is not None
    assert len(body["codigo_invitacion"]) == 6


def test_actualizar_vecino(client, auth_headers, db_session):
    v = Vecino(nombre="Antiguo", piso="2ºB", tipo="propietario")
    db_session.add(v)
    db_session.commit()
    db_session.refresh(v)

    res = client.patch(
        f"/api/vecinos/{v.id}",
        headers=auth_headers,
        json={"nombre": "Nuevo Nombre", "telefono": "666777888"},
    )
    assert res.status_code == 200
    assert res.json()["nombre"] == "Nuevo Nombre"
    assert res.json()["telefono"] == "666777888"


def test_eliminar_vecino(client, auth_headers, db_session):
    v = Vecino(nombre="Borrar", piso="9ºZ", tipo="propietario")
    db_session.add(v)
    db_session.commit()
    db_session.refresh(v)

    res = client.delete(f"/api/vecinos/{v.id}", headers=auth_headers)
    assert res.status_code == 204

    res_get = client.get(f"/api/vecinos/{v.id}", headers=auth_headers)
    assert res_get.status_code == 404


def test_crear_vecino_como_conserje_devuelve_403(client, conserje_headers):
    res = client.post(
        "/api/vecinos/",
        headers=conserje_headers,
        json={"nombre": "Intento", "piso": "5ºD"},
    )
    assert res.status_code == 403


def test_listar_vecinos_paginacion(client, auth_headers, db_session):
    for i in range(5):
        db_session.add(Vecino(nombre=f"Vecino {i}", piso=f"{i}ºA", tipo="propietario"))
    db_session.commit()

    res = client.get("/api/vecinos/?skip=0&limit=3", headers=auth_headers)
    assert res.status_code == 200
    assert len(res.json()) == 3
