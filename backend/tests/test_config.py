def test_config_devuelve_nombre_de_comunidad_sin_autenticacion(client):
    """
    /api/config debe ser accesible sin token: la pantalla de login todavía
    no tiene ninguno cuando necesita mostrar el nombre de la comunidad.
    """
    res = client.get("/api/config")
    assert res.status_code == 200
    assert "community_name" in res.json()


def test_config_usa_el_valor_por_defecto_si_no_hay_variable_de_entorno(client, monkeypatch):
    monkeypatch.delenv("COMMUNITY_NAME", raising=False)
    res = client.get("/api/config")
    assert res.status_code == 200
    assert res.json()["community_name"]  # no vacío


def test_config_refleja_la_variable_de_entorno(client, monkeypatch):
    monkeypatch.setenv("COMMUNITY_NAME", "Residencial Los Almendros")
    res = client.get("/api/config")
    assert res.json()["community_name"] == "Residencial Los Almendros"
