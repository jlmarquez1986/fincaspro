"""Tests adicionales de llaves."""

from models import Llave, Vecino


def test_listar_llaves(client, auth_headers, db_session):
    db_session.add(Llave(nombre="Garaje", codigo="LL-G01"))
    db_session.add(Llave(nombre="Azotea", codigo="LL-A01"))
    db_session.commit()

    res = client.get("/api/llaves/", headers=auth_headers)
    assert res.status_code == 200
    assert len(res.json()) == 2
    # Debe venir ordenado por código
    codigos = [llave["codigo"] for llave in res.json()]
    assert codigos == sorted(codigos)


def test_eliminar_llave(client, auth_headers, db_session):
    llave = Llave(nombre="Borrar", codigo="LL-DEL")
    db_session.add(llave)
    db_session.commit()
    db_session.refresh(llave)

    res = client.delete(f"/api/llaves/{llave.id}", headers=auth_headers)
    assert res.status_code == 204


def test_prestar_llave_a_vecino(client, auth_headers, db_session):
    v = Vecino(nombre="Prestatario", piso="5ºE", tipo="propietario")
    db_session.add(v)
    db_session.commit()
    db_session.refresh(v)

    llave = Llave(nombre="Trastero", codigo="LL-T01")
    db_session.add(llave)
    db_session.commit()
    db_session.refresh(llave)

    res = client.patch(
        f"/api/llaves/{llave.id}/prestar",
        headers=auth_headers,
        json={"prestada_a": "Prestatario", "vecino_id": v.id},
    )
    assert res.status_code == 200
    assert res.json()["estado"] == "prestada"
