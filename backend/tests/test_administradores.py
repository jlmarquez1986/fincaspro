"""Tests CRUD de administradores/empresas externas."""

from models import Administrador


def test_listar_administradores(client, auth_headers, db_session):
    db_session.add(Administrador(entidad="Fontanería SL", nombre="Juan"))
    db_session.add(Administrador(entidad="Electricidad SL", nombre="Pedro"))
    db_session.commit()

    res = client.get("/api/administradores/", headers=auth_headers)
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_filtrar_administradores_por_entidad(client, auth_headers, db_session):
    db_session.add(Administrador(entidad="Fontanería SL", nombre="Juan"))
    db_session.add(Administrador(entidad="Electricidad SL", nombre="Pedro"))
    db_session.commit()

    res = client.get("/api/administradores/?entidad=Fontanería SL", headers=auth_headers)
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["entidad"] == "Fontanería SL"


def test_crear_administrador(client, auth_headers):
    res = client.post(
        "/api/administradores/",
        headers=auth_headers,
        json={
            "entidad": "Limpieza SL",
            "nombre": "María",
            "telefono": "666111222",
            "email": "limpieza@test.com",
        },
    )
    assert res.status_code == 201
    assert res.json()["entidad"] == "Limpieza SL"


def test_actualizar_administrador(client, auth_headers, db_session):
    a = Administrador(entidad="Vieja", nombre="Antiguo")
    db_session.add(a)
    db_session.commit()
    db_session.refresh(a)

    res = client.patch(
        f"/api/administradores/{a.id}",
        headers=auth_headers,
        json={"entidad": "Nueva", "nombre": "Actualizado"},
    )
    assert res.status_code == 200
    assert res.json()["entidad"] == "Nueva"


def test_eliminar_administrador(client, auth_headers, db_session):
    a = Administrador(entidad="Borrar", nombre="X")
    db_session.add(a)
    db_session.commit()
    db_session.refresh(a)

    res = client.delete(f"/api/administradores/{a.id}", headers=auth_headers)
    assert res.status_code == 204


def test_crear_administrador_como_conserje_devuelve_403(client, conserje_headers):
    res = client.post(
        "/api/administradores/",
        headers=conserje_headers,
        json={"entidad": "Hack", "nombre": "X"},
    )
    assert res.status_code == 403
