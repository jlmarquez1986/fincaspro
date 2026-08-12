"""
Tests del Portal del Vecino.
Endpoints exclusivos para vecinos autenticados.
"""

from models import Aviso, Paquete, Ticket, Vecino


def test_portal_login_exitoso(client, vecino_user):
    res = client.post(
        "/api/portal/login",
        json={"email": "vecino_test@email.com", "password": "MiClaveVecino1"},
    )
    assert res.status_code == 200
    body = res.json()
    assert "access_token" in body
    assert body["vecino"]["piso"] == "3ºA"


def test_portal_login_password_incorrecta(client, vecino_user):
    res = client.post(
        "/api/portal/login",
        json={"email": "vecino_test@email.com", "password": "mala"},
    )
    assert res.status_code == 401


def test_portal_login_cuenta_no_activada(client, db_session):
    from security import hash_password

    v = Vecino(
        nombre="Inactivo",
        email="inactivo@test.com",
        piso="10ºA",
        tipo="propietario",
        password=hash_password("cualquiera"),
        portal_activo="false",
    )
    db_session.add(v)
    db_session.commit()

    res = client.post(
        "/api/portal/login",
        json={"email": "inactivo@test.com", "password": "cualquiera"},
    )
    assert res.status_code == 403


def test_mi_perfil_devuelve_datos_vecino(client, vecino_headers, vecino_user):
    res = client.get("/api/portal/me", headers=vecino_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["nombre"] == vecino_user.nombre
    assert body["piso"] == vecino_user.piso


def test_vecino_crea_ticket_desde_portal(client, vecino_headers, vecino_user):
    res = client.post(
        "/api/portal/tickets",
        headers=vecino_headers,
        data={
            "asunto": "Fuga en mi baño",
            "descripcion": "Gotea el grifo",
            "categoria": "fontaneria",
            "prioridad": "alta",
        },
    )
    assert res.status_code == 201
    body = res.json()
    assert body["asunto"] == "Fuga en mi baño"
    assert body["piso"] == vecino_user.piso
    assert body["vecino_id"] == vecino_user.id


def test_vecino_ve_sus_tickets(client, vecino_headers, db_session, vecino_user):
    t = Ticket(asunto="Solo mío", categoria="otros", vecino_id=vecino_user.id)
    db_session.add(t)
    db_session.commit()

    res = client.get("/api/portal/mis-tickets", headers=vecino_headers)
    assert res.status_code == 200
    asuntos = [tk["asunto"] for tk in res.json()]
    assert "Solo mío" in asuntos


def test_vecino_ve_sus_paquetes(client, vecino_headers, db_session, vecino_user):
    p = Paquete(vecino_id=vecino_user.id, remitente="Amazon", tamanio="pequeno")
    db_session.add(p)
    db_session.commit()

    res = client.get("/api/portal/mis-paquetes", headers=vecino_headers)
    assert res.status_code == 200
    remitentes = [pkg["remitente"] for pkg in res.json()]
    assert "Amazon" in remitentes


def test_vecino_ve_avisos_comunidad(client, vecino_headers, db_session):
    db_session.add(Aviso(titulo="Junta urgente", contenido="Mañana a las 20h", activo="true"))
    db_session.add(Aviso(titulo="Viejo", contenido="Archivado", activo="false"))
    db_session.commit()

    res = client.get("/api/portal/avisos", headers=vecino_headers)
    assert res.status_code == 200
    titulos = [a["titulo"] for a in res.json()]
    assert "Junta urgente" in titulos
    assert "Viejo" not in titulos
