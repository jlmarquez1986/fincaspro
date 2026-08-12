"""Tests CRUD de usuarios (solo admin)."""

from models.usuario import Usuario


def test_listar_usuarios_como_admin(client, auth_headers):
    res = client.get("/api/usuarios/", headers=auth_headers)
    assert res.status_code == 200
    usernames = [u["username"] for u in res.json()]
    assert "admin_test" in usernames


def test_listar_usuarios_como_conserje_devuelve_403(client, conserje_headers):
    res = client.get("/api/usuarios/", headers=conserje_headers)
    assert res.status_code == 403


def test_crear_usuario(client, auth_headers):
    res = client.post(
        "/api/usuarios/",
        headers=auth_headers,
        json={
            "nombre": "Nuevo Usuario",
            "username": "nuevo_user",
            "email": "nuevo@test.com",
            "password": "PasswordSegura1",
            "rol": "conserje",
        },
    )
    assert res.status_code == 201
    assert res.json()["username"] == "nuevo_user"
    assert res.json()["rol"] == "conserje"
    assert "password" not in res.json()


def test_no_se_puede_crear_usuario_username_duplicado(client, auth_headers):
    client.post(
        "/api/usuarios/",
        headers=auth_headers,
        json={
            "nombre": "Duplicado",
            "username": "dup_user",
            "email": "dup1@test.com",
            "password": "12345678",
        },
    )
    res = client.post(
        "/api/usuarios/",
        headers=auth_headers,
        json={
            "nombre": "Otro",
            "username": "dup_user",
            "email": "dup2@test.com",
            "password": "12345678",
        },
    )
    assert res.status_code == 400


def test_no_se_puede_crear_usuario_email_duplicado(client, auth_headers):
    client.post(
        "/api/usuarios/",
        headers=auth_headers,
        json={
            "nombre": "Primero",
            "username": "user_a",
            "email": "mismo@email.com",
            "password": "12345678",
        },
    )
    res = client.post(
        "/api/usuarios/",
        headers=auth_headers,
        json={
            "nombre": "Segundo",
            "username": "user_b",
            "email": "mismo@email.com",
            "password": "12345678",
        },
    )
    assert res.status_code == 400


def test_actualizar_usuario(client, auth_headers, db_session):
    u = Usuario(
        nombre="Actualizar",
        username="update_me",
        email="update@test.com",
        password="hash",
        rol="conserje",
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)

    res = client.patch(
        f"/api/usuarios/{u.id}",
        headers=auth_headers,
        json={"nombre": "Actualizado", "rol": "admin"},
    )
    assert res.status_code == 200
    assert res.json()["nombre"] == "Actualizado"
    assert res.json()["rol"] == "admin"


def test_eliminar_usuario(client, auth_headers, db_session):
    u = Usuario(
        nombre="Borrar",
        username="delete_me",
        email="delete@test.com",
        password="hash",
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)

    res = client.delete(f"/api/usuarios/{u.id}", headers=auth_headers)
    assert res.status_code == 204
