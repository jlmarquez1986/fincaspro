"""Tests de teléfonos de interés."""

from models import TelefonoInteres


def test_listar_telefonos(client, auth_headers, db_session):
    db_session.add(TelefonoInteres(nombre="Urgencias", telefono="112"))
    db_session.commit()

    res = client.get("/api/telefonos-interes/", headers=auth_headers)
    assert res.status_code == 200
    assert len(res.json()) >= 1


def test_filtrar_por_categoria(client, auth_headers, db_session):
    db_session.add(TelefonoInteres(nombre="Urgencias", telefono="112", categoria="emergencia"))
    db_session.add(TelefonoInteres(nombre="Pizzería", telefono="123", categoria="ocio"))
    db_session.commit()

    res = client.get("/api/telefonos-interes/?categoria=emergencia", headers=auth_headers)
    assert res.status_code == 200
    assert all(t["categoria"] == "emergencia" for t in res.json())


def test_crear_telefono(client, auth_headers):
    res = client.post(
        "/api/telefonos-interes/",
        headers=auth_headers,
        json={"nombre": "Farmacia", "telefono": "666555444", "categoria": "salud"},
    )
    assert res.status_code == 201
    assert res.json()["nombre"] == "Farmacia"


def test_actualizar_telefono(client, auth_headers, db_session):
    t = TelefonoInteres(nombre="Viejo", telefono="000")
    db_session.add(t)
    db_session.commit()
    db_session.refresh(t)

    res = client.patch(
        f"/api/telefonos-interes/{t.id}",
        headers=auth_headers,
        json={"nombre": "Nuevo", "telefono": "111"},
    )
    assert res.status_code == 200
    assert res.json()["nombre"] == "Nuevo"


def test_eliminar_telefono(client, auth_headers, db_session):
    t = TelefonoInteres(nombre="Borrar", telefono="000")
    db_session.add(t)
    db_session.commit()
    db_session.refresh(t)

    res = client.delete(f"/api/telefonos-interes/{t.id}", headers=auth_headers)
    assert res.status_code == 204


def test_crear_telefono_como_conserje_devuelve_403(client, conserje_headers):
    res = client.post(
        "/api/telefonos-interes/",
        headers=conserje_headers,
        json={"nombre": "Hack", "telefono": "000"},
    )
    assert res.status_code == 403
