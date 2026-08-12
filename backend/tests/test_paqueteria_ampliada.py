"""Tests adicionales de paquetería."""

from models import Paquete, Vecino


def test_listar_paquetes(client, auth_headers, db_session):
    v = Vecino(nombre="Con paquetes", piso="1ºA", tipo="propietario")
    db_session.add(v)
    db_session.commit()
    db_session.refresh(v)

    db_session.add(Paquete(vecino_id=v.id, remitente="Amazon", estado="pendiente"))
    db_session.add(Paquete(vecino_id=v.id, remitente="AliExpress", estado="entregado"))
    db_session.commit()

    res = client.get("/api/paqueteria/", headers=auth_headers)
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_filtro_paquetes_por_estado(client, auth_headers, db_session):
    v = Vecino(nombre="Filtro", piso="2ºB", tipo="propietario")
    db_session.add(v)
    db_session.commit()
    db_session.refresh(v)

    db_session.add(Paquete(vecino_id=v.id, remitente="A", estado="pendiente"))
    db_session.add(Paquete(vecino_id=v.id, remitente="B", estado="entregado"))
    db_session.commit()

    res = client.get("/api/paqueteria/?estado=entregado", headers=auth_headers)
    assert res.status_code == 200
    assert all(p["estado"] == "entregado" for p in res.json())


def test_marcar_paquete_entregado(client, auth_headers, db_session):
    v = Vecino(nombre="Entrega", piso="3ºC", tipo="propietario")
    db_session.add(v)
    db_session.commit()
    db_session.refresh(v)

    p = Paquete(vecino_id=v.id, remitente="Correos", estado="pendiente")
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)

    res = client.patch(f"/api/paqueteria/{p.id}/entregar", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["estado"] == "entregado"
    assert res.json()["entregado_en"] is not None


def test_eliminar_paquete(client, auth_headers, db_session):
    v = Vecino(nombre="Borrar", piso="4ºD", tipo="propietario")
    db_session.add(v)
    db_session.commit()
    db_session.refresh(v)

    p = Paquete(vecino_id=v.id, remitente="Borrar")
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)

    res = client.delete(f"/api/paqueteria/{p.id}", headers=auth_headers)
    assert res.status_code == 204
