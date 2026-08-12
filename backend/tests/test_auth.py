def test_login_exitoso_devuelve_token_y_usuario(client, admin_user):
    res = client.post(
        "/api/auth/login",
        data={"username": "admin_test", "password": "clave_segura_123"},
    )
    assert res.status_code == 200
    body = res.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"

    # Regresión: el frontend depende de este campo para poder loguear al
    # usuario. Si desaparece, el login "no hace nada" en el navegador
    # aunque el backend responda 200.
    assert "usuario" in body
    assert body["usuario"]["username"] == "admin_test"
    assert body["usuario"]["rol"] == "admin"
    assert "password" not in body["usuario"]


def test_login_password_incorrecta_devuelve_401(client, admin_user):
    res = client.post(
        "/api/auth/login",
        data={"username": "admin_test", "password": "password-incorrecta"},
    )
    assert res.status_code == 401


def test_login_usuario_inexistente_devuelve_401(client):
    res = client.post(
        "/api/auth/login",
        data={"username": "no_existo", "password": "cualquiera"},
    )
    assert res.status_code == 401


def test_endpoint_protegido_sin_token_devuelve_401(client):
    res = client.get("/api/tickets/")
    assert res.status_code == 401


def test_endpoint_protegido_con_token_valido_funciona(client, auth_headers):
    res = client.get("/api/tickets/", headers=auth_headers)
    assert res.status_code == 200
