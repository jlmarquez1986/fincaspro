"""Tests del módulo de piscina (carnets, invitaciones, registros)."""

from models import CarnetPiscina, InvitacionPiscina, Vecino


def test_listar_carnets(client, auth_headers, db_session):
    v = Vecino(nombre="Con carnet", piso="1ºA", tipo="propietario")
    db_session.add(v)
    db_session.commit()
    db_session.refresh(v)
    db_session.add(CarnetPiscina(vecino_id=v.id, numero_carnet="CP-001"))
    db_session.commit()

    res = client.get("/api/piscina/carnets", headers=auth_headers)
    assert res.status_code == 200
    assert len(res.json()) >= 1


def test_crear_carnet_como_admin(client, auth_headers, db_session):
    v = Vecino(nombre="Nadador", piso="2ºB", tipo="propietario")
    db_session.add(v)
    db_session.commit()
    db_session.refresh(v)

    res = client.post(
        "/api/piscina/carnets",
        headers=auth_headers,
        json={"vecino_id": v.id, "numero_carnet": "CP-002"},
    )
    assert res.status_code == 201
    assert res.json()["numero_carnet"] == "CP-002"
    assert res.json()["activo"] is True


def test_crear_carnet_vecino_inexistente_devuelve_400(client, auth_headers):
    res = client.post(
        "/api/piscina/carnets",
        headers=auth_headers,
        json={"vecino_id": 99999, "numero_carnet": "CP-999"},
    )
    assert res.status_code == 400


def test_verificar_carnet_valido(client, auth_headers, db_session):
    v = Vecino(nombre="Verificar", piso="3ºC", tipo="propietario")
    db_session.add(v)
    db_session.commit()
    db_session.refresh(v)
    db_session.add(CarnetPiscina(vecino_id=v.id, numero_carnet="CP-003", activo=True))
    db_session.commit()

    res = client.get("/api/piscina/carnets/verificar/CP-003", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["valido"] is True
    assert res.json()["nombre"] == "Verificar"


def test_verificar_carnet_invalido(client, auth_headers):
    res = client.get("/api/piscina/carnets/verificar/NOEXISTE", headers=auth_headers)
    assert res.status_code == 404


def test_saldo_invitaciones_nuevo_mes(client, auth_headers, db_session):
    v = Vecino(nombre="Invitado", piso="4ºD", tipo="propietario")
    db_session.add(v)
    db_session.commit()
    db_session.refresh(v)

    res = client.get(f"/api/piscina/invitaciones/vecino/{v.id}", headers=auth_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["total"] == 10  # default
    assert body["usadas"] == 0
    assert body["disponibles"] == 10


def test_configurar_invitaciones_como_admin(client, auth_headers):
    res = client.patch(
        "/api/piscina/invitaciones/config?nuevo_total=15",
        headers=auth_headers,
    )
    assert res.status_code == 200
    assert "15" in res.json()["mensaje"]


def test_configurar_invitaciones_como_conserje_devuelve_403(client, conserje_headers):
    res = client.patch(
        "/api/piscina/invitaciones/config?nuevo_total=20",
        headers=conserje_headers,
    )
    assert res.status_code == 403


def test_registrar_acceso_piscina(client, auth_headers, db_session):
    v = Vecino(nombre="Acceso", piso="5ºE", tipo="propietario")
    db_session.add(v)
    db_session.commit()
    db_session.refresh(v)
    db_session.add(CarnetPiscina(vecino_id=v.id, numero_carnet="CP-005", activo=True))
    db_session.commit()

    res = client.post(
        "/api/piscina/registros",
        headers=auth_headers,
        json={"vecino_id": v.id, "tipo": "entrada"},
    )
    assert res.status_code == 201
    assert res.json()["tipo"] == "entrada"


def test_registrar_acceso_sin_carnet_devuelve_403(client, auth_headers, db_session):
    v = Vecino(nombre="Sin carnet", piso="6ºF", tipo="propietario")
    db_session.add(v)
    db_session.commit()
    db_session.refresh(v)

    res = client.post(
        "/api/piscina/registros",
        headers=auth_headers,
        json={"vecino_id": v.id, "tipo": "entrada"},
    )
    assert res.status_code == 403


def test_registrar_acceso_invitacion_sin_saldo(client, auth_headers, db_session):
    from database import utcnow

    v = Vecino(nombre="Sin saldo", piso="7ºG", tipo="propietario")
    db_session.add(v)
    db_session.commit()
    db_session.refresh(v)
    db_session.add(CarnetPiscina(vecino_id=v.id, numero_carnet="CP-006", activo=True))
    db_session.commit()

    # Agotar invitaciones del MES ACTUAL (el endpoint busca mes/año actual)
    hoy = utcnow()
    inv = InvitacionPiscina(
        vecino_id=v.id,
        mes=hoy.month,
        anio=hoy.year,
        total_asignadas=1,
        usadas=1,
    )
    db_session.add(inv)
    db_session.commit()

    res = client.post(
        "/api/piscina/registros",
        headers=auth_headers,
        json={"vecino_id": v.id, "tipo": "invitacion", "nombre_invitado": "Pepe"},
    )
    assert res.status_code == 400


def test_listar_registros(client, auth_headers, db_session):
    v = Vecino(nombre="Registro", piso="8ºH", tipo="propietario")
    db_session.add(v)
    db_session.commit()
    db_session.refresh(v)
    db_session.add(CarnetPiscina(vecino_id=v.id, numero_carnet="CP-007", activo=True))
    db_session.commit()

    client.post(
        "/api/piscina/registros",
        headers=auth_headers,
        json={"vecino_id": v.id, "tipo": "entrada"},
    )

    res = client.get("/api/piscina/registros", headers=auth_headers)
    assert res.status_code == 200
    assert len(res.json()) >= 1
