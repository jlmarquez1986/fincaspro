import os
import sys
from logging.config import fileConfig

from alembic import context  # type: ignore[attr-defined]
from sqlalchemy import engine_from_config, pool

# ── OBTENER LA RUTA DE LA RAÍZ DEL PROYECTO ──────────
# __file__ es la ruta de este archivo (env.py)
# Subimos dos niveles para llegar a la raíz del proyecto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Añadir la raíz al sys.path SIEMPRE al principio
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# ── IMPORTAR BASE DESDE DATABASE ──────────────────────
# Ahora Python buscará en la raíz del proyecto
try:
    import models  # noqa: F401 — necesario para que Base.metadata conozca todas las tablas
    from database import Base
except ImportError as e:
    # Si falla, mostramos información para depurar
    print(f"❌ Error: No se pudo importar 'database' o 'models' ({e})")
    print(f"📁 BASE_DIR = {BASE_DIR}")
    print(f"📁 Archivos en BASE_DIR: {os.listdir(BASE_DIR)}")
    print(
        f"🔧 ¿Existe 'database.py' en la raíz?"
        f"{os.path.exists(os.path.join(BASE_DIR, 'database.py'))}"
    )
    raise

config = context.config

# Alembic debe utilizar la misma base de datos que la aplicación.
# DATABASE_URL se inyecta por entorno en producción y puede seguir
# utilizando el valor de alembic.ini como fallback en desarrollo.
database_url = os.getenv("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
