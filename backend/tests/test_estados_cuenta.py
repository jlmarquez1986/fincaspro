"""Tests de estados de cuenta (solo admin)."""

from models import EstadoCuenta


def test_listar_estados(client, auth_headers, db_session):
    db_session.add(EstadoCuenta(entidad="Comunidad", mes=1, anio=2026, saldo_final=1000))
    db_session.commit()

    res = client.get("/api/estados-cuenta/", headers=auth_headers)
    assert res.status_code == 200
    assert len(res.json()) >= 1


def test_filtrar_estados_por_mes_anio(client, auth_headers, db_session):
    db_session.add(EstadoCuenta(entidad="Comunidad", mes=1, anio=2026))
    db_session.add(EstadoCuenta(entidad="Comunidad", mes=2, anio=2026))
    db_session.commit()

    res = client.get("/api/estados-cuenta/?mes=2&anio=2026", headers=auth_headers)
    assert res.status_code == 200
    assert all(e["mes"] == 2 for e in res.json())


def test_crear_estado(client, auth_headers):
    res = client.post(
        "/api/estados-cuenta/",
        headers=auth_headers,
        json={
            "entidad": "Comunidad",
            "mes": 3,
            "anio": 2026,
            "saldo_inicial": 500,
            "ingresos": 200,
            "gastos": 100,
            "saldo_final": 600,
        },
    )
    assert res.status_code == 201
    assert res.json()["saldo_final"] == 600


def test_no_duplicar_mes_anio_entidad(client, auth_headers, db_session):
    db_session.add(EstadoCuenta(entidad="Comunidad", mes=4, anio=2026))
    db_session.commit()

    res = client.post(
        "/api/estados-cuenta/",
        headers=auth_headers,
        json={"entidad": "Comunidad", "mes": 4, "anio": 2026},
    )
    assert res.status_code == 400


def test_actualizar_estado(client, auth_headers, db_session):
    e = EstadoCuenta(entidad="Comunidad", mes=5, anio=2026, saldo_final=100)
    db_session.add(e)
    db_session.commit()
    db_session.refresh(e)

    res = client.patch(
        f"/api/estados-cuenta/{e.id}",
        headers=auth_headers,
        json={
            "entidad": "Comunidad",
            "mes": 5,
            "anio": 2026,
            "saldo_final": 200,
            "observaciones": "Actualizado",
        },
    )
    assert res.status_code == 200
    assert res.json()["saldo_final"] == 200


def test_eliminar_estado(client, auth_headers, db_session):
    e = EstadoCuenta(entidad="Comunidad", mes=6, anio=2026)
    db_session.add(e)
    db_session.commit()
    db_session.refresh(e)

    res = client.delete(f"/api/estados-cuenta/{e.id}", headers=auth_headers)
    assert res.status_code == 204
