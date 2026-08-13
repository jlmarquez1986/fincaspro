# 🏢 FincasPro

Sistema de gestión de fincas y conserjería para comunidades de vecinos — panel de administración para el staff (conserje/administrador) y un portal independiente para que cada vecino consulte sus propios tickets, paquetes y avisos.

[![CI](https://github.com/TU_USUARIO/fincaspro/actions/workflows/ci.yml/badge.svg)](https://github.com/TU_USUARIO/fincaspro/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.12%20%7C%203.13-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-blue)

> **Estado actual (agosto de 2026):** desarrollo avanzado y preparación para producción. El backend tiene **109 tests pasando** y **87,56 % de cobertura**; el CI valida backend, frontend y la build de Docker de producción automáticamente en cada push, con subida de cobertura a Codecov confirmada y funcionando.

> Reemplaza `TU_USUARIO` en el badge de arriba por tu usuario/organización de GitHub una vez subas el repo.

![Captura de FincasPro](./Captura%20de%20pantalla%202026-06-15%20164351.png)

---

## Qué resuelve

Una comunidad de vecinos necesita gestionar averías, paquetería, llaves y avisos sin depender de un grupo de WhatsApp. FincasPro separa dos experiencias:

- **Panel de staff** (conserje/administrador): tickets con foto adjunta, control de llaves, registro de paquetería, avisos a toda la comunidad, notificaciones automáticas por email.
- **Portal del vecino**: cada vecino entra con su propia cuenta y solo ve sus datos — no puede ver tickets, paquetes ni información de otros vecinos.

## Stack técnico

| Capa | Tecnología |
|------|-----------|
| Backend | FastAPI · SQLAlchemy · Pydantic v2 · JWT (python-jose) · bcrypt |
| Frontend | React 18 · Vite · PWA (vite-plugin-pwa) |
| Base de datos | SQLite (desarrollo) — migrable a PostgreSQL cambiando `DATABASE_URL` |
| Email | aiosmtplib + MailHog (desarrollo) |
| Tests | pytest + FastAPI TestClient, base de datos aislada en memoria |
| CI | GitHub Actions (tests de backend + build de frontend en cada push) |
| Contenedores | Docker + docker-compose |

## Características

- 🔐 Autenticación JWT separada para staff y vecinos (tokens y scopes distintos)
- 📸 Tickets de incidencias con foto adjunta
- 📦 Registro y seguimiento de paquetería
- 🔑 Control de llaves prestadas
- 🏷️ Nombre de la comunidad personalizable (una variable de entorno, sin tocar código)
- 📢 Avisos con notificación automática por email a toda la comunidad
- 🏠 Portal del vecino: solo lectura de sus propios datos, con autoservicio para reportar averías
- 🧪 109 tests automatizados + 87,56 % de cobertura + CI en GitHub Actions
- 🧹 Calidad de código: Ruff, MyPy, Pyright y ESLint
- 📱 Instalable como app en el móvil (PWA) — icono en pantalla de inicio, pantalla completa, sin tienda de apps
- 🐳 Entorno de desarrollo reproducible con Docker Compose; la variante de producción se documentará durante el paso 9.

---

## Estructura del proyecto

```
fincaspro/
├── .github/workflows/ci.yml    # Lint, tipos, tests, cobertura y build automáticos
├── .gitattributes                # Normaliza finales de línea a LF
├── pyproject.toml                # Ruff, MyPy, Pyright, pytest y coverage
├── docker-compose.yml
├── backend/                    # API FastAPI
│   ├── main.py
│   ├── database.py             # SQLAlchemy + SQLite
│   ├── auth.py                 # JWT + bcrypt + política de contraseñas
│   ├── schemas.py              # Modelos Pydantic
│   ├── seed.py                 # Datos de prueba
│   ├── models/                 # Modelos SQLAlchemy
│   ├── routers/                # Endpoints de la API
│   ├── services/
│   │   └── email_service.py
│   ├── tests/                  # pytest — auth, tickets, permisos
│   └── uploads/tickets/        # Fotos subidas
│
└── frontend/                   # React 18 + Vite
    └── src/
        ├── App.jsx
        └── api/client.js
```

---

## Calidad, tests y CI/CD

El proyecto incorpora un pipeline de integración continua en `.github/workflows/ci.yml`. Se ejecuta en los `push` y `pull_request` dirigidos a `main` y `develop`.

### Backend

El job de backend se valida con Python 3.12 y 3.13 e incluye:

1. Instalación de dependencias de desarrollo.
2. `ruff check backend/`.
3. `ruff format --check backend/`.
4. MyPy.
5. Pyright.
6. Pytest con cobertura mínima del 80 %.
7. Publicación opcional de cobertura en Codecov.

### Frontend

El job de frontend utiliza Node.js 20 e incluye:

1. `npm ci`.
2. ESLint.
3. `npm run build`.

### Estado de la suite

En la última verificación completa del proyecto:

- **109/109 tests** pasan.
- **87,56 % de cobertura**.
- Ruff: limpio.
- MyPy: limpio.
- Pyright: limpio.
- ESLint: 0 errores (quedan únicamente warnings no bloqueantes).
- Build de producción de Vite: correcto.

La configuración de Ruff, MyPy, Pyright, pytest y coverage está centralizada en `pyproject.toml`. Las migraciones generadas de Alembic quedan excluidas de Ruff y de los analizadores estáticos cuando corresponde.

`.gitattributes` fuerza la normalización de finales de línea a LF para evitar diferencias entre Windows, Linux y GitHub Actions.

> **Codecov:** la subida de cobertura es opcional (si `CODECOV_TOKEN` no está configurado, el workflow no falla por este paso gracias a `fail_ci_if_error: false`), pero ya está configurada y verificada: el log del CI confirma la subida correcta del reporte a `app.codecov.io`.

## Cómo ejecutarlo

### Opción A — Docker para desarrollo (recomendado actualmente)

```bash
git clone https://github.com/TU_USUARIO/fincaspro.git
cd fincaspro
docker-compose up --build
```

| Servicio | URL |
|----------|-----|
| Frontend | http://localhost:5173 |
| API (docs incluidos) | http://localhost:8000/docs |
| MailHog (ver emails enviados) | http://localhost:8025 |

### Opción B — Sin Docker

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
python seed.py                 # carga datos de prueba
uvicorn main:app --reload
```

**Frontend** (en otra terminal):
```bash
cd frontend
npm install
npm run dev
```

### Datos de prueba (creados por `seed.py`)

| Rol | Usuario | Contraseña |
|-----|---------|------------|
| Admin | `admin` | `admin123` |
| Conserje | `conserje` | `conserje123` |
| Vecino (portal) | `maria@email.com` | `vecino123` |
| Vecino (portal) | `pedro@email.com` | `vecino123` |

---

## Instalar en el móvil (PWA)

FincasPro es una **Progressive Web App**: se puede instalar en el móvil directamente desde el navegador, sin pasar por Google Play ni App Store. Queda con su propio icono, abre a pantalla completa y carga instantáneamente aunque la conexión sea mala.

**Requisito importante:** fuera de `localhost`, la instalación solo funciona servida por **HTTPS** — es una exigencia de seguridad de los navegadores, no algo configurable en la app. Si despliegas en un dominio propio con Nginx/Vercel/Netlify detrás de HTTPS, esto ya viene resuelto.

**Android (Chrome):**
1. Abre la web del frontend en Chrome.
2. Aparecerá un banner "Añadir a pantalla de inicio", o desde el menú ⋮ → *Instalar app*.

**iPhone/iPad (Safari):**
1. Abre la web en Safari (no funciona desde Chrome en iOS).
2. Botón compartir (□↑) → *Añadir a pantalla de inicio*.

Una vez instalada, el icono queda en el launcher como cualquier otra app, y las actualizaciones del sistema se aplican solas la siguiente vez que se abre (`registerType: 'autoUpdate'`).

> **Nota:** con `docker-compose up` (o `npm run dev`) el frontend corre en modo desarrollo, y la PWA está desactivada a propósito en ese modo — un service worker cacheando código a medias mientras programas da más problemas que ventajas. Para probar la instalación real: `cd frontend && npm run build && npm run preview`, y abre esa URL desde el móvil (en la misma red) o despliega el contenido de `frontend/dist` en un hosting con HTTPS.

## Tests

```bash
cd backend
pip install -r requirements.txt   # incluye pytest y httpx
pytest tests/ -v
```

Los tests corren contra una base de datos SQLite en memoria, completamente aislada de `fincaspro.db` — no hace falta levantar nada más y no se pierden datos al ejecutarlos.

**Estado validado:** 109/109 tests pasan y la cobertura es del 87,56 %. El CI también comprueba Ruff, MyPy, Pyright, ESLint y el build de producción del frontend.

---

## Seguridad

- El `SECRET_KEY` para firmar los JWT se lee de una variable de entorno (`backend/.env`, ver `.env.example`) y es obligatorio en producción (`ENVIRONMENT=production`); en desarrollo se genera uno aleatorio si no se define.
- Contraseñas hasheadas con bcrypt, con una longitud mínima exigida al crearlas.
- Tokens de staff y de vecino usan JWT y *scopes* separados — un token de vecino no sirve para acceder a endpoints de staff, ni viceversa.
- Cada vecino solo puede leer o crear datos vinculados a su propio `vecino_id`, validado en el backend (no solo ocultado en el frontend).

## Documentación adicional

- [**REQUIREMENTS.md**](./REQUIREMENTS.md) — documento completo de arquitectura, requisitos funcionales/no funcionales, modelo de datos, API, flujos del sistema y guía para desarrolladores.
- [Configuración de email (MailHog, Brevo, SendGrid...) y comandos de Docker](./docs/EMAIL_Y_DESPLIEGUE.md)

## Registro de cambios recientes

- **13 ago 2026** — Confirmado en el log de GitHub Actions que la subida de cobertura a Codecov funciona correctamente con `CODECOV_TOKEN` configurado (firma GPG verificada, reporte subido a `app.codecov.io`). Refactorización del frontend: `AuthContext.jsx` se dividió en `context/AuthContext.js` (contexto) y `context/AuthProvider.jsx` (proveedor), y se añadió `utils/date.js`. Actualización de dependencias del frontend: `npm audit fix` + subida manual de `react-router-dom` a `7.18.2`, resolviendo 6 de las 8 vulnerabilidades detectadas. Quedan 2 (moderada/alta) ligadas a `esbuild`/`vite ≤6.4.2`, que solo se resuelven saltando a Vite 8 — de momento bloqueado por un conflicto de peer dependencies con `@vitejs/plugin-react@6` y pospuesto a una sesión propia.
- **12 ago 2026 — Paso 8 del roadmap (CI/CD con GitHub Actions)** completado: se corrigió un bug de ruta al instalar `requirements` en `ci.yml`, se añadió el job de frontend (lint + build) que faltaba, se normalizaron los finales de línea CRLF→LF con `.gitattributes`, se arreglaron 2 errores reales de MyPy en `security.py`, se eliminó un `pyrightconfig.json` que pisaba la configuración de `pyproject.toml`, se instaló y configuró ESLint en el frontend (existía el script pero no la dependencia) corrigiendo 7 errores reales, y se añadieron `pytest-asyncio` y `pyright` a `requirements-dev.txt`.

## Próximos pasos (roadmap)

### Preparación para producción
- [x] Docker de producción separado del entorno de desarrollo (`docker-compose.prod.yml`)
- [x] Build multi-stage del frontend y servidor estático con Nginx
- [x] Healthchecks y configuración de servicios
- [x] Revisión de persistencia de base de datos y archivos subidos (volúmenes)
- [x] CORS y variables de entorno específicas de producción (`.env.production.example`)
- [ ] HTTPS / reverse proxy — pendiente añadir una capa TLS delante de Nginx antes de publicar en Internet
- [ ] Revisión final de secretos y configuración de despliegue en el hosting real

### Evolución funcional y técnica
- [ ] Migrar de SQLite a PostgreSQL (Alembic ya gestiona el esquema, migración de motor pendiente)
- [ ] Sistema de permisos por acción en lugar de roles fijos
- [ ] Pantalla de administración para crear cuentas de staff
- [ ] Registro de auditoría de acciones
- [ ] Rate limiting y bloqueo tras varios intentos de login fallidos
- [ ] Multi-comunidad
- [ ] Paginación en listados de la API
- [ ] Migrar frontend a Vite 8 (bloqueado por conflicto de peer dependencies con `@vitejs/plugin-react@6`; hasta entonces quedan 2 vulnerabilidades moderadas/altas en `esbuild`/`vite` que solo afectan al servidor de desarrollo, no a producción)

## Licencia

MIT — ver [LICENSE](./LICENSE).

## Docker de producción

FincasPro mantiene separados los entornos de desarrollo y producción.

### Desarrollo

`docker-compose.yml` conserva el entorno cómodo para trabajar con hot reload, Vite y MailHog.

### Producción

La configuración `docker-compose.prod.yml` utiliza:

- FastAPI + Uvicorn sin `--reload`.
- Alembic para aplicar migraciones al iniciar el backend.
- React compilado con Vite y servido mediante Nginx.
- Nginx como reverse proxy para `/api/` y `/uploads/`.
- Health checks para backend y frontend.
- Volúmenes persistentes para la base de datos SQLite y los archivos subidos.
- Variables de entorno para secretos, SMTP, CORS y configuración de la comunidad.
- Imágenes multi-stage en el frontend para no incluir Node.js en la imagen final.

Preparación:

```bash
cp .env.production.example .env.production
# Edita .env.production y sustituye todos los valores sensibles.

docker compose --env-file .env.production -f docker-compose.prod.yml up -d --build
```

Comprobaciones básicas:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml ps
docker compose --env-file .env.production -f docker-compose.prod.yml logs -f backend
```

El backend expone `/health` internamente y Nginx publica la aplicación en el puerto configurado mediante `HTTP_PORT`.

> Para publicar FincasPro en Internet todavía debe añadirse una capa TLS/HTTPS delante de Nginx (por ejemplo, un proxy o balanceador gestionado por el proveedor de infraestructura). No se considera HTTPS implementado hasta completar esa fase.

## Migraciones de base de datos

El esquema de producción se gestiona con Alembic. El arranque del contenedor ejecuta `alembic upgrade head` cuando `MIGRATE_ON_STARTUP=true`.

La migración inicial contiene el esquema actual y la migración posterior añade el campo `alcance` de los tickets. En producción no se ejecuta `Base.metadata.create_all()`; ese comportamiento queda reservado al desarrollo local.

Comandos útiles desde `backend/`:

```bash
alembic current
alembic history
alembic upgrade head
```

Antes de generar una nueva migración se recomienda comprobar el estado del esquema y revisar manualmente el script generado.

## Calidad y CI/CD

El workflow de GitHub Actions ejecuta actualmente:

1. Ruff lint.
2. Ruff format check.
3. MyPy.
4. Pyright.
5. Pytest + cobertura mínima del 80 %.
6. ESLint.
7. Build de producción del frontend.
8. Validación y build de las imágenes Docker de producción.

La última validación funcional registrada del backend mantiene 109 tests pasando y una cobertura del 87,56 %. Los valores deben volver a comprobarse después de cada cambio relevante.