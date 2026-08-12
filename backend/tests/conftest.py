"""
Fixtures compartidas para toda la suite de tests.

Usamos una base de datos SQLite en memoria, completamente separada de
fincaspro.db, para que correr los tests nunca toque ni borre datos reales.
"""

import os
import sys
from pathlib import Path

# Añadir la carpeta raíz del backend al PYTHONPATH para que los imports
# funcionen correctamente cuando se ejecuta pytest desde cualquier lugar.
# Esto es necesario porque los módulos (auth, database, main, etc.) están
# en la raíz del proyecto, no dentro de tests/.
BACKEND_ROOT = str(Path(__file__).parent.parent)
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("SECRET_KEY", "test-secret-key-solo-para-tests")
os.environ.setdefault("COMMUNITY_NAME", "Comunidad de Test")

import pytest
from database import Base, get_db
from fastapi.testclient import TestClient
from main import app
from models.usuario import Usuario
from models.vecino import Vecino
from rate_limiter import limiter
from security import hash_password
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# El rate limiter usa estado global compartido entre tests (misma IP de
# TestClient). Sin desactivarlo, tests que hacen varias peticiones seguidas
# empiezan a recibir 429 según el orden/cantidad de tests ejecutados antes.
limiter.enabled = False

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── Usuarios ──────────────────────────────────────────────────────────


@pytest.fixture()
def admin_user(db_session):
    user = Usuario(
        nombre="Admin de Prueba",
        username="admin_test",
        email="admin_test@fincaspro.local",
        password=hash_password("clave_segura_123"),
        rol="admin",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def admin_token(client, admin_user):
    res = client.post(
        "/api/auth/login",
        data={"username": "admin_test", "password": "clave_segura_123"},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


@pytest.fixture()
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture()
def conserje_user(db_session):
    user = Usuario(
        nombre="Conserje de Prueba",
        username="conserje_test",
        email="conserje_test@fincaspro.local",
        password=hash_password("clave_segura_123"),
        rol="conserje",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def conserje_token(client, conserje_user):
    res = client.post(
        "/api/auth/login",
        data={"username": "conserje_test", "password": "clave_segura_123"},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


@pytest.fixture()
def conserje_headers(conserje_token):
    return {"Authorization": f"Bearer {conserje_token}"}


# ── Vecinos ───────────────────────────────────────────────────────────


@pytest.fixture()
def vecino_user(db_session):
    """Vecino con portal activo y contraseña hasheada."""
    v = Vecino(
        nombre="Vecino de Prueba",
        email="vecino_test@email.com",
        piso="3ºA",
        tipo="propietario",
        password=hash_password("MiClaveVecino1"),
        portal_activo="true",
    )
    db_session.add(v)
    db_session.commit()
    db_session.refresh(v)
    return v


@pytest.fixture()
def vecino_token(client, vecino_user):
    res = client.post(
        "/api/portal/login",
        json={"email": "vecino_test@email.com", "password": "MiClaveVecino1"},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


@pytest.fixture()
def vecino_headers(vecino_token):
    return {"Authorization": f"Bearer {vecino_token}"}


@pytest.fixture()
def vecino_sin_activar(db_session):
    """Vecino sin portal activo, con código de invitación."""
    v = Vecino(
        nombre="Piso sin activar",
        piso="7ºB",
        tipo="propietario",
        codigo_invitacion="INV7B",
    )
    db_session.add(v)
    db_session.commit()
    db_session.refresh(v)
    return v
