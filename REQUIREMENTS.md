# FincasPro — Documento de Requisitos y Arquitectura

> Sistema de gestión de fincas y conserjería. Este documento describe el sistema completo: qué hace, cómo está construido, y cómo instalarlo, extenderlo y mantenerlo.

**Versión del documento:** 1.1 · **Versión del sistema:** FincasPro v2.0.x · **Estado:** desarrollo avanzado / preparación para producción · **Última actualización:** agosto de 2026

---

## Índice

1. [Introducción del proyecto](#1-introducción-del-proyecto)
2. [Arquitectura del sistema](#2-arquitectura-del-sistema)
3. [Requisitos funcionales](#3-requisitos-funcionales)
4. [Requisitos no funcionales](#4-requisitos-no-funcionales)
5. [Base de datos](#5-base-de-datos)
6. [API](#6-api)
7. [Frontend](#7-frontend)
8. [Backend](#8-backend)
9. [Flujos completos del sistema](#9-flujos-completos-del-sistema)
10. [Instalación](#10-instalación)
11. [Roadmap](#11-roadmap)
12. [Calidad de código, tests y CI/CD](#12-calidad-de-código-tests-y-cicd)
13. [Guía para desarrolladores](#13-guía-para-desarrolladores)

---

## 1. Introducción del proyecto

### 1.1 Objetivo

FincasPro digitaliza la gestión diaria de una comunidad de vecinos, sustituyendo el cuaderno de conserjería y el grupo de WhatsApp por un sistema con dos entradas separadas:

- Un **panel de staff** (conserje/administrador) para gestionar incidencias, paquetería, llaves y avisos.
- Un **portal del vecino** de solo sus propios datos, con autoservicio para reportar averías.

### 1.2 Alcance

**Incluido en la versión actual:**
- Gestión de incidencias (tickets) con foto adjunta, categoría, prioridad y comentarios.
- Registro y entrega de paquetería, con notificación por email al destinatario.
- Control de llaves prestadas (a quién, desde cuándo).
- Avisos de comunidad, notificados por email a todos los vecinos con correo registrado.
- Portal del vecino con login propio: consulta de tickets, paquetes y avisos propios, y alta de nuevas incidencias.
- Autenticación JWT separada para staff y vecinos (dos esquemas de token distintos, sin superposición de permisos).
- Registro (alta) de cuenta de portal por parte del propio vecino, sobre un piso ya dado de alta por el staff.

**Explícitamente fuera de alcance en esta versión** (ver [Roadmap](#11-roadmap)):
- Creación de cuentas de staff desde la interfaz (hoy solo vía script `seed.py` o acceso directo a la base de datos).
- Pagos, facturación, actas de reuniones o reservas de zonas comunes.
- Multi-comunidad (una instalación gestiona una única comunidad).
- Notificaciones push o en tiempo real (solo email).

### 1.3 Público objetivo

| Perfil | Uso |
|---|---|
| **Conserje** | Operación diaria: registrar incidencias, paquetes, préstamos de llaves. |
| **Administrador de finca** | Todo lo del conserje, más borrado de registros y gestión de la ficha de vecinos. |
| **Vecino** | Consulta de sus propios tickets, paquetes y avisos; reporte de averías desde el portal. |
| **Desarrollador** | Extender el sistema — este documento es su punto de entrada técnico. |

---

## 2. Arquitectura del sistema

### 2.1 Visión general

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────┐
│   React (Vite)   │  HTTP   │   FastAPI (REST)  │  SQL    │   SQLite    │
│   frontend/src    │ ──────▶ │   backend/         │ ──────▶ │  fincaspro.db│
└─────────────────┘  JWT    └──────────────────┘         └─────────────┘
                                      │
                                      │ SMTP (aiosmtplib)
                                      ▼
                              ┌───────────────┐
                              │ MailHog (dev)  │
                              │ o proveedor    │
                              │ real (prod)    │
                              └───────────────┘
```

El backend expone una API REST bajo `/api`. No hay renderizado del lado del servidor: el frontend es una SPA que consume la API vía `fetch`, con dos tokens JWT independientes guardados en `localStorage` (`token` para staff, `vecino_token` para el portal).

### 2.2 Estructura completa de carpetas

```
fincaspro/
├── .github/workflows/ci.yml     # Tests + build automáticos (GitHub Actions)
├── docker-compose.yml           # Orquesta backend + frontend + MailHog
├── docs/EMAIL_Y_DESPLIEGUE.md   # Configuración de email y comandos Docker
├── LICENSE                      # MIT
├── README.md                    # Puerta de entrada para humanos
├── REQUIREMENTS.md              # Este documento
│
├── backend/
│   ├── main.py                  # Punto de entrada FastAPI, monta routers y CORS
│   ├── database.py              # Engine de SQLAlchemy + sesión + Base declarativa
│   ├── auth.py                  # JWT, hashing bcrypt, dependencias de autenticación
│   ├── schemas.py               # Modelos Pydantic (contratos de entrada/salida de la API)
│   ├── seed.py                  # Script para poblar la base de datos con datos de prueba
│   ├── requirements.txt         # Dependencias Python
│   ├── Dockerfile
│   ├── .env.example             # Plantilla de variables de entorno
│   │
│   ├── models/                  # Entidades SQLAlchemy (una tabla = un archivo)
│   │   ├── __init__.py          # Reexporta todos los modelos
│   │   ├── usuario.py           # Staff: admin / conserje
│   │   ├── vecino.py            # Vecinos (ficha + credenciales de portal)
│   │   ├── ticket.py            # Incidencias + Comentario (tabla hija)
│   │   ├── paquete.py           # Paquetería
│   │   ├── llave.py             # Llaves prestables
│   │   └── aviso.py             # Avisos de comunidad
│   │
│   ├── routers/                 # Un router = un recurso de la API
│   │   ├── auth.py              # Login de staff
│   │   ├── vecinos.py           # CRUD de vecinos + registro de portal
│   │   ├── tickets.py           # CRUD de incidencias + comentarios
│   │   ├── paqueteria.py        # Alta y entrega de paquetes
│   │   ├── llaves.py            # Alta, préstamo y devolución de llaves
│   │   ├── avisos.py            # Alta y archivado de avisos
│   │   └── portal.py            # Endpoints exclusivos del vecino autenticado
│   │
│   ├── services/
│   │   └── email_service.py     # Plantillas y envío de email (aiosmtplib)
│   │
│   ├── tests/                   # pytest — base de datos en memoria, aislada
│   │   ├── conftest.py          # Fixtures: cliente de test, usuario admin, headers
│   │   ├── test_auth.py
│   │   ├── test_tickets.py
│   │   ├── test_portal.py
│   │   └── test_paqueteria_avisos.py
│   │
│   └── uploads/tickets/         # Fotos subidas (servidas como estáticos en /uploads)
│
└── frontend/
    ├── index.html                # Carga fuentes (Fraunces/Inter), meta tags PWA, monta React
    ├── vite.config.js            # Proxy de /api y /uploads + configuración PWA (manifest, service worker)
    ├── Dockerfile
    ├── public/                   # Iconos de la PWA (192/512/maskable/apple-touch/favicon)
    └── src/
        ├── main.jsx               # Punto de entrada React
        ├── App.jsx                # Todas las pantallas y componentes (ver sección 7)
        ├── index.css              # Sistema de diseño (tokens, componentes)
        └── api/client.js          # Cliente HTTP: un método por endpoint
```

### 2.3 Explicación de cada módulo

| Módulo | Responsabilidad |
|---|---|
| `main.py` | Arranca la app, registra middleware CORS, monta cada router bajo su prefijo `/api/...`, sirve `/uploads` como estáticos, expone `/api/dashboard` con los contadores del panel principal. |
| `database.py` | Crea el `engine` de SQLAlchemy a partir de `DATABASE_URL`, la fábrica de sesiones `SessionLocal` y la dependencia `get_db()` que inyecta una sesión por request y la cierra al terminar. |
| `auth.py` | Hashing de contraseñas (bcrypt), emisión y verificación de JWT, y las dos dependencias de autenticación (`get_current_user` para staff, `get_current_vecino` para el portal) que routers y endpoints usan como *guard*. |
| `schemas.py` | Define qué forma tienen los datos que entran y salen de la API (Pydantic). Es el contrato entre frontend y backend — si un campo no está aquí, la API no lo acepta ni lo devuelve. |
| `models/` | El esquema real de la base de datos (SQLAlchemy ORM). Cada clase es una tabla. |
| `routers/` | La lógica de cada endpoint: valida permisos, consulta/modifica la base de datos, dispara notificaciones. |
| `services/email_service.py` | Aísla toda la lógica de envío de email (SMTP, plantillas HTML/texto) para que los routers no sepan nada de cómo se manda un correo. |
| `frontend/src/App.jsx` | Todas las pantallas de la SPA: login, dashboard, cada módulo del staff, y el portal del vecino. |
| `frontend/src/api/client.js` | Única capa que sabe hacer `fetch` — añade el token correcto según la ruta y lanza un `Error` legible si la API responde con un fallo. |

### 2.4 Flujo de funcionamiento (alto nivel)

1. El navegador carga la SPA de React.
2. El usuario elige "Staff" o "Portal del Vecino" en la pantalla de selección.
3. Inicia sesión → el backend valida credenciales y devuelve un JWT + los datos del usuario/vecino.
4. El frontend guarda el token en `localStorage` y lo adjunta en cada petición siguiente (`Authorization: Bearer ...`).
5. Cada pantalla pide sus datos a la API (`GET`), y cada acción (crear ticket, prestar llave, etc.) hace un `POST`/`PATCH`/`DELETE`.
6. Ciertas acciones (nuevo ticket, nuevo paquete, nuevo aviso) disparan un email al vecino afectado o a toda la comunidad, de forma asíncrona y sin bloquear la respuesta si el envío falla.

---

## 3. Requisitos funcionales

Cada funcionalidad se describe con su flujo, quién puede usarla, y de qué otros módulos depende.

### 3.1 Autenticación de staff

**Descripción paso a paso:**
1. El usuario introduce usuario y contraseña en la pantalla de login de staff.
2. El frontend envía `POST /api/auth/login` como formulario (`OAuth2PasswordRequestForm`).
3. El backend busca el usuario por `username`, verifica la contraseña con bcrypt.
4. Si es válida, genera un JWT firmado (`sub: username`, expira en 8h) y devuelve el usuario (sin la contraseña).
5. El frontend guarda el token y los datos del usuario, y navega al panel.

**Caso de uso:** conserje entra cada mañana para revisar incidencias pendientes.
**Depende de:** módulo `usuarios` (tabla), `auth.py`.

### 3.2 Gestión de incidencias (tickets)

**Descripción paso a paso:**
1. Staff pulsa "Nueva avería", rellena asunto, categoría, prioridad, piso, vecino afectado (opcional) y foto (opcional).
2. `POST /api/tickets/con-foto` (multipart) crea el ticket con estado `pendiente`.
3. El ticket aparece en la lista, filtrable por estado (pendiente / en_proceso / resuelto).
4. Staff puede cambiar el estado o la prioridad (`PATCH /api/tickets/{id}`), añadir comentarios (`POST /api/tickets/{id}/comentarios`), o borrarlo (`DELETE`, solo admin).
5. Un vecino puede reportar su propia avería desde el portal (`POST /api/portal/tickets`) — el `vecino_id` y `piso` se asignan automáticamente desde su sesión, nunca desde un campo editable.

**Caso de uso:** una gotera en el 3ºB — el vecino la reporta con foto desde el portal; el conserje la ve en su panel, la marca "en_proceso" y luego "resuelto".
**Depende de:** módulo `vecinos` (para asignar el ticket a un piso/vecino), `services/email_service.py` (import presente, pero **sin llamada activa** — ver [Roadmap](#11-roadmap)).

### 3.3 Paquetería

**Descripción paso a paso:**
1. Staff registra la llegada de un paquete: destinatario (obligatorio), remitente, nº de seguimiento (`tracking`), tamaño.
2. `POST /api/paqueteria/` crea el registro con estado `pendiente` y notifica por email al vecino si tiene correo.
3. El paquete aparece en la lista de pendientes.
4. Cuando el vecino lo recoge, staff pulsa "Entregar" → `PATCH /api/paqueteria/{id}/entregar`, que cambia el estado a `entregado` y registra la fecha.

**Caso de uso:** llega un pedido de Amazon para el 5ºA; el conserje lo registra, el sistema avisa por email, y cuando el vecino pasa a recogerlo se marca como entregado.
**Depende de:** módulo `vecinos` (destinatario obligatorio), `services/email_service.py`.

> **Nota conocida:** el campo `tracking` se guarda pero **no se muestra** todavía ni en la tabla del staff ni en "Mis Paquetes" del portal — ver [Roadmap](#11-roadmap).

### 3.4 Control de llaves

**Descripción paso a paso:**
1. Staff da de alta una llave con nombre y código único (`POST /api/llaves/`).
2. Para prestarla: `PATCH /api/llaves/{id}/prestar` con a quién se presta — la llave pasa a estado `prestada` y se registra la fecha.
3. No se puede volver a prestar una llave que ya está prestada (validación en el backend, no solo en el frontend).
4. Al devolverla: `PATCH /api/llaves/{id}/devolver`, que limpia quién la tenía y vuelve a `disponible`.

**Caso de uso:** una empresa de mantenimiento necesita la llave del cuarto de contadores; el conserje la presta y queda constancia de quién la tiene.
**Depende de:** módulo `vecinos` (opcional, si se presta a un vecino registrado).

### 3.5 Avisos de comunidad

**Descripción paso a paso:**
1. Staff crea un aviso con título, contenido y tipo (`info` / `aviso` / `urgente`).
2. `POST /api/avisos/` lo guarda como activo y notifica por email a **todos** los vecinos con correo registrado.
3. El aviso aparece en el portal de cada vecino y en el panel de staff.
4. Se puede archivar (`PATCH /api/avisos/{id}/archivar`), lo que lo oculta sin borrarlo.

**Caso de uso:** corte de agua programado — el administrador publica el aviso y toda la comunidad lo recibe por email a la vez.
**Depende de:** módulo `vecinos` (destinatarios), `services/email_service.py`.

### 3.6 Portal del vecino

**Descripción paso a paso:**
1. El staff da de alta el piso del vecino (sin credenciales todavía) desde el panel de "Vecinos".
2. El vecino activa su cuenta desde el login del portal: indica su piso, nombre, email y elige contraseña (`POST /api/vecinos/portal/registro`). Solo funciona si el piso existe y no tiene ya una cuenta activa.
3. A partir de ahí, inicia sesión con email/contraseña (`POST /api/portal/login`), recibe un JWT propio con `vecino_id` en el payload (no `sub`, para que nunca sea intercambiable con un token de staff).
4. Desde el portal ve **solo** sus tickets, paquetes y avisos de la comunidad, y puede reportar nuevas averías.

**Caso de uso:** un vecino nuevo se muda, la conserjería da de alta su piso, y él mismo activa su acceso al portal sin depender de que el conserje le cree una contraseña.
**Depende de:** módulo `vecinos`, `auth.py` (esquema de token separado).

### 3.7 Dashboard

**Descripción:** `GET /api/dashboard` devuelve cuatro contadores (tickets abiertos, paquetes pendientes, llaves prestadas, tickets resueltos) que alimentan las tarjetas de resumen del panel principal del staff.
**Depende de:** módulos `tickets`, `paqueteria`, `llaves`.

### 3.8 Matriz de dependencias entre módulos

```
usuarios (staff)  ──▶  todos los routers de staff (autenticación)
vecinos            ──▶  tickets, paqueteria, llaves (opcional), avisos (destinatarios), portal
tickets            ──▶  email_service (importado, sin uso activo)
paqueteria         ──▶  email_service
avisos             ──▶  email_service
portal             ──▶  vecinos, tickets, paqueteria, avisos (solo lectura + alta de tickets)
```

---

## 4. Requisitos no funcionales

### 4.1 Seguridad

- **Autenticación:** JWT (HS256) con expiración de 8 horas. Dos esquemas independientes — staff (`sub: username`) y vecino (`vecino_id`) — de modo que un token de un tipo nunca es válido para endpoints del otro.
- **Contraseñas:** hasheadas con bcrypt (nunca en texto plano); longitud mínima de 8 caracteres, validada en `auth.hash_password()`.
- **Clave de firma (`SECRET_KEY`):** se lee de variable de entorno. En `ENVIRONMENT=production`, el arranque falla si no está definida — nunca hay una clave por defecto insegura en producción. En desarrollo se genera una aleatoria por proceso si falta.
- **Autorización por rol:** `role_required("admin")` restringe operaciones destructivas (borrar tickets, borrar vecinos) solo a administradores.
- **Aislamiento de datos del vecino:** cada endpoint del portal filtra explícitamente por `vecino_id` extraído del token — nunca de un parámetro que el cliente pueda manipular.
- **CORS:** restringido a los orígenes de desarrollo conocidos (`localhost:5173`, `localhost:3000`); debe ampliarse con el dominio real al desplegar en producción.
- **Manejo de errores:** los fallos de envío de email se capturan y registran (`logging`), sin filtrar detalles internos ni tumbar la petición que los originó.

### 4.2 Rendimiento

- Backend asíncrono (FastAPI sobre Starlette/uvicorn); los endpoints que no dependen de I/O externo son de baja latencia sobre SQLite en desarrollo.
- El envío de email es la única operación de red externa por request y está aislado con `try/except` para no penalizar el resto del flujo si el SMTP tarda o falla.
- No hay paginación en los listados (`GET /api/tickets/`, etc.) — aceptable para el volumen de una comunidad pequeña/mediana, pero es el primer cuello de botella esperable al crecer (ver Roadmap).

### 4.3 Escalabilidad

- SQLite es adecuado para una única comunidad de tamaño pequeño-mediano. `DATABASE_URL` es la única pieza que cambia para migrar a PostgreSQL — el resto del código (SQLAlchemy ORM) no necesita tocarse para el CRUD actual.
- El sistema está diseñado para **una comunidad por instalación** (no multi-tenant); repartir varias comunidades exige un cambio de modelo de datos (ver Roadmap).
- Las fotos se guardan en disco local — migrar a almacenamiento de objetos (S3/MinIO) es un cambio acotado a `routers/tickets.py` y `routers/portal.py`.

### 4.4 Compatibilidad

- **Backend:** Python 3.12 (probado también con 3.11 vía Docker); FastAPI 0.115, SQLAlchemy 2.0, Pydantic v2.
- **Frontend:** React 18 + Vite 5; sin dependencia de un navegador concreto, JavaScript moderno estándar (ES2020+).
- **Contenedores:** imágenes oficiales `python:3.11-slim` y `node:20`; orquestado con `docker-compose` v3.8.
- **Base de datos:** SQLite por defecto; compatible con PostgreSQL cambiando solo la cadena de conexión.
- **PWA:** instalable en Android (Chrome) e iOS (Safari) desde el navegador. Requiere HTTPS en cualquier dominio que no sea `localhost` — es una exigencia del propio navegador, no una opción de configuración de la app.

---

## 5. Base de datos

### 5.1 Diagrama de relaciones (texto)

```
usuarios                 vecinos
─────────                ─────────
id (PK)                  id (PK)
nombre                   nombre
username (unique)        email
email (unique)           telefono
password (hash)          piso
rol                      tipo
creado_en                password (hash, nullable)
                          portal_activo
                          creado_en
                              │
                              │ 1
              ┌───────────────┼───────────────┬────────────────┐
              │ N              │ N              │ N               │ N
              ▼                ▼                ▼                 ▼
          tickets          paquetes          llaves          (avisos: sin FK,
          ─────────        ─────────         ─────────        son globales)
          id (PK)          id (PK)           id (PK)
          asunto           remitente         nombre
          descripcion      vecino_id (FK)    codigo (unique)
          categoria        tracking          descripcion
          prioridad        tamanio           estado
          estado           estado            prestada_a
          piso             notificado        vecino_id (FK, nullable)
          vecino_id (FK,   recibido_en       desde
            nullable)      entregado_en
          asignado_a
          foto_path
          creado_en
          actualizado
              │
              │ 1
              ▼ N
         comentarios
         ─────────
         id (PK)
         ticket_id (FK)
         autor
         texto
         creado_en

avisos
─────────
id (PK)
titulo
contenido
tipo
activo
creado_en
```

### 5.2 Explicación de cada entidad

| Tabla | Propósito | Notas |
|---|---|---|
| **usuarios** | Cuentas de staff (admin/conserje). | `rol` distingue permisos; no tiene FK a nada. |
| **vecinos** | Ficha de cada piso **y**, opcionalmente, sus credenciales de portal. | `password` es `nullable`: un vecino puede existir sin cuenta de portal activa (`portal_activo = "false"`). |
| **tickets** | Incidencias/averías. | `vecino_id` es opcional — una avería en zona comunal no tiene vecino asociado. `foto_path` apunta a un archivo servido bajo `/uploads`. |
| **comentarios** | Hilo de comentarios de un ticket. | FK obligatoria a `tickets`; se borran en cascada solo si se implementa explícitamente (hoy no hay `ON DELETE CASCADE` configurado). |
| **paquetes** | Paquetería recibida. | `vecino_id` es **obligatorio** (a diferencia de tickets) — un paquete siempre tiene un destinatario. |
| **llaves** | Inventario de llaves prestables. | `codigo` es único; `vecino_id` es opcional porque una llave puede prestarse a alguien que no es vecino (ej. empresa externa) usando solo el campo `prestada_a`. |
| **avisos** | Comunicados a toda la comunidad. | Sin relación directa con `vecinos`: al crearse, se consulta la tabla de vecinos por email en el momento, no se guarda una relación persistente. |

### 5.3 Campos completos por tabla

<details>
<summary><strong>usuarios</strong></summary>

| Campo | Tipo | Restricciones |
|---|---|---|
| id | Integer | PK, autoincremental |
| nombre | String | NOT NULL |
| username | String | UNIQUE, NOT NULL |
| email | String | UNIQUE, NOT NULL |
| password | String | NOT NULL (hash bcrypt) |
| rol | String | default `"conserje"` (`admin` / `conserje`) |
| creado_en | DateTime | default `utcnow()` |
</details>

<details>
<summary><strong>vecinos</strong></summary>

| Campo | Tipo | Restricciones |
|---|---|---|
| id | Integer | PK |
| nombre | String | NOT NULL |
| email | String | nullable |
| telefono | String | nullable |
| piso | String | NOT NULL |
| tipo | String | default `"propietario"` (`propietario` / `inquilino`) |
| password | String | nullable (hash bcrypt, solo si activó el portal) |
| portal_activo | String | default `"false"` (`"true"`/`"false"` como texto, no booleano) |
| creado_en | DateTime | default `utcnow()` |
</details>

<details>
<summary><strong>tickets</strong></summary>

| Campo | Tipo | Restricciones |
|---|---|---|
| id | Integer | PK |
| asunto | String | NOT NULL |
| descripcion | Text | nullable |
| categoria | String | default `"otros"` |
| prioridad | String | default `"normal"` |
| estado | String | default `"pendiente"` (`pendiente`/`en_proceso`/`resuelto`) |
| piso | String | nullable |
| vecino_id | Integer | FK → vecinos.id, nullable |
| asignado_a | String | nullable |
| foto_path | String | nullable |
| creado_en | DateTime | default `utcnow()` |
| actualizado | DateTime | default y `onupdate` `utcnow()` |
</details>

<details>
<summary><strong>comentarios</strong></summary>

| Campo | Tipo | Restricciones |
|---|---|---|
| id | Integer | PK |
| ticket_id | Integer | FK → tickets.id, NOT NULL |
| autor | String | default `"Conserje"` |
| texto | Text | NOT NULL |
| creado_en | DateTime | default `utcnow()` |
</details>

<details>
<summary><strong>paquetes</strong></summary>

| Campo | Tipo | Restricciones |
|---|---|---|
| id | Integer | PK |
| remitente | String | nullable |
| vecino_id | Integer | FK → vecinos.id, NOT NULL |
| tracking | String | nullable |
| tamanio | String | default `"mediano"` |
| estado | String | default `"pendiente"` (`pendiente`/`entregado`) |
| notificado | String | default `"no"` |
| recibido_en | DateTime | default `utcnow()` |
| entregado_en | DateTime | nullable |
</details>

<details>
<summary><strong>llaves</strong></summary>

| Campo | Tipo | Restricciones |
|---|---|---|
| id | Integer | PK |
| nombre | String | NOT NULL |
| codigo | String | UNIQUE, NOT NULL |
| descripcion | String | nullable |
| estado | String | default `"disponible"` (`disponible`/`prestada`) |
| prestada_a | String | nullable |
| vecino_id | Integer | FK → vecinos.id, nullable |
| desde | DateTime | nullable |
</details>

<details>
<summary><strong>avisos</strong></summary>

| Campo | Tipo | Restricciones |
|---|---|---|
| id | Integer | PK |
| titulo | String | NOT NULL |
| contenido | Text | NOT NULL |
| tipo | String | default `"info"` (`info`/`aviso`/`urgente`) |
| activo | String | default `"true"` |
| creado_en | DateTime | default `utcnow()` |
</details>

---

## 6. API

Base URL: `/api`. Documentación interactiva autogenerada disponible en `/docs` (Swagger UI) y `/redoc` cuando el backend está corriendo.

### 6.1 Autenticación

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| POST | `/api/auth/login` | — | Login de staff. Body: `form-urlencoded` (`username`, `password`). |
| POST | `/api/auth/vecinos/login` | — | Login alternativo de vecino por OAuth2 form (no usado por el frontend actual; el portal usa `/api/portal/login`). |
| POST | `/api/portal/login` | — | Login del portal. Body JSON: `{email, password}`. |
| POST | `/api/vecinos/portal/registro` | — | Alta de cuenta de portal sobre un piso existente. Body JSON: `{piso, nombre, email, password}`. |

**Ejemplo — `POST /api/auth/login`**
```
Request (form-urlencoded):
  username=admin&password=admin123

Response 200:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "usuario": {
    "id": 1, "nombre": "Admin", "username": "admin",
    "email": "admin@fincaspro.local", "rol": "admin"
  }
}

Response 401:
{ "detail": "Usuario o contraseña incorrectos" }
```

### 6.2 Tickets (staff) — prefijo `/api/tickets`, requiere token de staff

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Lista tickets. Query opcional `?estado=pendiente`. |
| POST | `/con-foto` | Crea un ticket (`multipart/form-data`: `asunto`, `descripcion`, `categoria`, `prioridad`, `piso`, `vecino_id`, `asignado_a`, `foto`). |
| PATCH | `/{ticket_id}` | Actualiza `estado`, `asignado_a` y/o `prioridad`. |
| DELETE | `/{ticket_id}` | Borra un ticket. **Solo admin.** |
| POST | `/{ticket_id}/comentarios` | Añade un comentario. Body JSON: `{autor?, texto}`. |

**Ejemplo — `POST /api/tickets/con-foto`**
```
Response 201:
{
  "id": 12, "asunto": "Fuga de agua", "descripcion": "En el garaje",
  "categoria": "fontaneria", "prioridad": "urgente", "estado": "pendiente",
  "piso": "Garaje", "vecino_id": null, "asignado_a": null,
  "foto_path": "/uploads/tickets/8f1c...jpg",
  "creado_en": "2026-07-15T10:00:00", "actualizado": "2026-07-15T10:00:00"
}
```

### 6.3 Paquetería — prefijo `/api/paqueteria`, requiere token de staff

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Lista paquetes. Query opcional `?estado=pendiente`. |
| POST | `/` | Registra un paquete. Body JSON: `PaqueteCreate` (`vecino_id` obligatorio). |
| PATCH | `/{pkg_id}/entregar` | Marca como entregado. |
| DELETE | `/{pkg_id}` | Borra un registro de paquete. |

### 6.4 Llaves — prefijo `/api/llaves`, requiere token de staff

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Lista llaves. |
| POST | `/` | Crea una llave (`nombre`, `codigo` único, `descripcion?`). |
| PATCH | `/{llave_id}/prestar` | Presta la llave. Body: `{prestada_a, vecino_id?}`. Falla con 400 si ya está prestada. |
| PATCH | `/{llave_id}/devolver` | Marca como devuelta. |
| DELETE | `/{llave_id}` | Borra una llave. |

### 6.5 Avisos — prefijo `/api/avisos`, requiere token de staff

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Lista avisos activos. |
| POST | `/` | Crea un aviso y notifica por email a todos los vecinos con correo. |
| PATCH | `/{aviso_id}/archivar` | Desactiva el aviso (no lo borra). |

### 6.6 Vecinos — prefijo `/api/vecinos`, requiere token de staff (salvo el registro)

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/` | Staff | Lista vecinos, ordenados por piso. |
| POST | `/` | Staff | Da de alta un piso/vecino (sin credenciales de portal). |
| GET | `/{vecino_id}` | Staff | Ficha de un vecino. |
| DELETE | `/{vecino_id}` | Solo admin | Borra un vecino. |
| POST | `/portal/registro` | Pública | Activa la cuenta de portal de un piso ya existente. |

### 6.7 Portal del vecino — prefijo `/api/portal`, requiere token de vecino

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/login` | Login del vecino. |
| GET | `/me` | Perfil del vecino autenticado. |
| GET | `/mis-tickets` | Solo los tickets de ese vecino. |
| POST | `/tickets` | El vecino reporta su propia avería (`vecino_id`/`piso` autoasignados). Multipart, foto opcional. |
| GET | `/mis-paquetes` | Solo los paquetes de ese vecino. |
| GET | `/avisos` | Avisos activos de la comunidad. |

### 6.8 Dashboard

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/dashboard` | Contadores: tickets abiertos, paquetes pendientes, llaves prestadas, tickets resueltos. |

### 6.9 Convenciones generales de la API

- Todas las rutas devuelven JSON; los errores siguen el formato FastAPI estándar: `{"detail": "mensaje"}`.
- Los endpoints protegidos devuelven `401` sin token válido y `403` cuando el rol no tiene permiso.
- Los recursos no encontrados devuelven `404`.
- Las creaciones devuelven `201`; los borrados devuelven `204` sin cuerpo.

---

## 7. Frontend

Todo el frontend vive en `frontend/src/App.jsx` (una SPA de un solo archivo de componentes, sin router de terceros — la navegación es por estado de React).

### 7.1 Pantallas

| Pantalla | Componente | Acceso |
|---|---|---|
| Selector inicial | `Landing` | Pública — elige "Staff" o "Portal del Vecino". |
| Login de staff | `LoginStaff` | Pública. |
| Login / registro del portal | `LoginPortal` | Pública — alterna entre iniciar sesión y activar cuenta. |
| Dashboard | `Dashboard` | Staff — contadores + accesos rápidos. |
| Averías | `Tickets` | Staff — tabla filtrable, modal de creación con foto. |
| Paquetería | `Paqueteria` | Staff — tabla + modal de registro. |
| Llaves | `Llaves` | Staff — tabla + modal de préstamo. |
| Avisos | `Avisos` | Staff — lista + modal de creación. |
| Vecinos | `Vecinos` | Staff — listado de fichas. |
| Portal del vecino | `PortalVecino` | Vecino — sus tickets/paquetes/avisos + botón "Reportar avería". |

### 7.2 Componentes reutilizables

- `Badge` — pastilla de color según estado (`pendiente`, `resuelto`, etc.), mapea a las clases CSS `.badge-*`.
- `Sidebar` — navegación lateral del panel de staff, con contadores en vivo (`badges`) por sección.
- `fmtDate` — utilidad de formateo de fechas, no un componente visual.

### 7.3 Navegación

No hay `react-router`: la pantalla activa se controla con estado local en el componente raíz (`landing`, `authMode`, `user`, `vecino`, y `page` para la sección del panel de staff). El `Sidebar` cambia `page`; el layout general decide qué renderizar según si hay `user` (staff) o `vecino` (portal) en sesión.

> **Bug corregido:** el selector inicial (`Landing`) tiene dos opciones — "Staff" y "Portal del Vecino" — pero originalmente `onSelect` descartaba qué opción se había elegido y siempre mostraba el login de staff, sin importar cuál se pulsara. `LoginPortal` era inalcanzable desde la interfaz. Se corrigió añadiendo el estado `authMode` (`"staff"` | `"portal"`), fijado por `Landing.onSelect(type)` y usado para decidir qué pantalla de login mostrar.

### 7.4 Gestión de estado

- Sin librería de estado global (ni Redux ni Zustand): cada pantalla carga sus propios datos con `useEffect` + `api.*` al montar.
- La sesión (`token`/`user` o `vecino_token`/`vecino`) vive en `localStorage`, leída al arrancar la app para decidir si mostrar login o panel directamente.
- Los formularios de creación (tickets, paquetes, llaves, avisos, reporte de avería del vecino) son estado local del componente, sin persistencia hasta el submit.

---

## 8. Backend

### 8.1 Servicios

`services/email_service.py` centraliza toda la lógica de envío: construye el mensaje (texto y HTML) y lo envía vía `aiosmtplib`. Expone una función por tipo de evento: `notify_new_ticket`, `notify_ticket_status_change`, `notify_new_package`, `notify_new_aviso`, `notify_key_return_reminder`. Todas son `async` y deben ser `await`-eadas desde un endpoint también `async def` — nunca desde uno síncrono (ver nota de diseño más abajo).

### 8.2 Controladores (routers)

Cada router sigue el mismo patrón: recibe el payload validado por Pydantic, opera contra la sesión de base de datos inyectada por `Depends(get_db)`, y devuelve un modelo de salida también validado por Pydantic (`response_model=...`). La autorización se resuelve por dependencias (`Depends(get_current_user)`, `Depends(get_current_vecino)`, `Depends(role_required("admin"))`) — nunca comprobaciones manuales dispersas en el cuerpo del endpoint.

### 8.3 Lógica de negocio relevante

- **Un vecino nunca puede escribir datos de otro:** en cada endpoint del portal, el filtro por `vecino_id` sale del token, no de un parámetro de la petición.
- **Una llave prestada no puede volver a prestarse** hasta que se devuelve explícitamente.
- **El registro de portal es idempotente por piso:** si el piso ya tiene `portal_activo = "true"`, se rechaza un segundo registro.
- **Los fallos de notificación no deben afectar a la operación principal:** registrar un paquete o crear un aviso tiene éxito aunque el servidor SMTP esté caído — el error se registra en el log, no se propaga al cliente.

### 8.4 Validaciones

| Validación | Dónde |
|---|---|
| Formato de archivo de foto (`.jpg`, `.jpeg`, `.png`, `.webp`) | `routers/tickets.py`, `routers/portal.py` |
| Longitud mínima de contraseña (8 caracteres) | `auth.hash_password()` |
| Código de llave único | `routers/llaves.py` (comprobación explícita antes de insertar) |
| Piso existente y no duplicado al registrar portal | `routers/vecinos.py` |
| Rol requerido para operaciones destructivas | `auth.role_required()` |
| Tipos y campos obligatorios de cada payload | Pydantic (`schemas.py`), automático en cada request |

> **Nota de diseño (para quien extienda el proyecto):** los endpoints que envían email deben declararse `async def` y usar `await notify_...(...)` dentro de un `try/except`. Usar `asyncio.create_task(...)` dentro de un endpoint **síncrono** (`def`) falla con `RuntimeError: no running event loop`, porque FastAPI ejecuta los endpoints síncronos en un hilo de threadpool sin bucle de eventos activo. Este fue un bug real detectado y corregido en `paqueteria.py` y `avisos.py` — hay tests de regresión en `tests/test_paqueteria_avisos.py` que lo cubren.

> **Nota de diseño — zonas horarias:** los modelos guardan las fechas con `datetime.utcnow()` (UTC "naive", sin zona horaria adjunta) — es la práctica correcta para no mezclar husos horarios en el almacenamiento. El bug real estaba en la *serialización*: si la API devuelve esa fecha tal cual, sin indicar que es UTC, el navegador de quien la recibe la interpreta como si YA estuviera en su hora local, desplazando la hora mostrada por su propio huso horario (2 horas de más o de menos en España en verano, por ejemplo). La solución: `schemas.UTCModel` es una clase base con un `field_validator` que marca cualquier datetime "naive" como UTC antes de serializarlo, así la respuesta JSON siempre lleva el sufijo de zona horaria (`+00:00`). Con eso, `toLocaleString()` en el frontend convierte correctamente a la hora local de quien esté usando la app, sea cual sea su país. Cualquier schema `*Out` nuevo que devuelva un campo `datetime` debe heredar de `UTCModel` (ver `schemas.py`) para no reintroducir el mismo bug. Dentro de los emails (texto plano, sin navegador que convierta nada) se usa `services.email_service.format_local()`, que convierte explícitamente a la zona horaria de `APP_TIMEZONE` (variable de entorno, por defecto `Europe/Madrid`). Hay tests de regresión en `tests/test_zonas_horarias.py`.

---

## 9. Flujos completos del sistema

### 9.1 Flujo: alta de incidencia hasta su resolución

```
Vecino/Staff                Frontend                    Backend                      DB / Email
     │                          │                            │                            │
     │  rellena formulario      │                            │                            │
     ├─────────────────────────▶│                            │                            │
     │                          │ POST /tickets/con-foto      │                            │
     │                          │ (o /portal/tickets)         │                            │
     │                          ├───────────────────────────▶│                            │
     │                          │                            │ INSERT ticket (pendiente)  │
     │                          │                            ├───────────────────────────▶│
     │                          │                            │◀───────────────────────────┤
     │                          │◀───────────────────────────┤                            │
     │  ve el ticket en su lista│  201 + ticket creado        │                            │
     │◀─────────────────────────┤                            │                            │
     │                          │                            │                            │
     │  staff cambia estado     │                            │                            │
     ├─────────────────────────▶│ PATCH /tickets/{id}         │                            │
     │                          ├───────────────────────────▶│ UPDATE estado               │
     │                          │                            ├───────────────────────────▶│
     │  vecino ve el nuevo       │◀───────────────────────────┤                            │
     │  estado en su portal      │                            │                            │
     │◀─────────────────────────┤                            │                            │
```

### 9.2 Flujo: activación de cuenta de portal

```
1. Staff → panel "Vecinos" → crea el piso (sin contraseña)      [POST /api/vecinos/]
2. Vecino → login del portal → "¿Aún no tienes cuenta?"
3. Vecino → rellena piso + nombre + email + contraseña           [POST /api/vecinos/portal/registro]
4. Backend valida: ¿existe el piso? ¿no tiene ya cuenta activa?
   → si falla: 400 con motivo claro
   → si OK: guarda password (hash) y marca portal_activo = "true"
5. Vecino → inicia sesión con su email y contraseña               [POST /api/portal/login]
6. Backend emite JWT con {vecino_id} → Vecino entra a su portal
```

### 9.3 Flujo: notificación por email (paquete o aviso)

```
1. Staff registra el paquete/aviso            → se guarda en BD primero (commit)
2. Backend intenta enviar el email (await, dentro de try/except)
   → si el SMTP falla: se registra en el log, la petición igualmente responde 201
   → si el SMTP funciona: el vecino recibe el correo (o toda la comunidad, si es un aviso)
3. El frontend recibe 201 en cualquier caso y cierra el modal, refresca la lista
```

---

## 10. Instalación

### 10.1 Requisitos

- Python 3.12 (o 3.11)
- Node.js 20
- Docker + Docker Compose (opcional, pero recomendado)

### 10.2 Variables de entorno (`backend/.env`, ver `.env.example`)

| Variable | Obligatoria | Descripción |
|---|---|---|
| `ENVIRONMENT` | No (default `development`) | `production` obliga a definir `SECRET_KEY`. |
| `SECRET_KEY` | Sí en producción | Clave de firma de los JWT. Generar con `python -c "import secrets; print(secrets.token_hex(32))"`. |
| `DATABASE_URL` | No (default SQLite local) | Cadena de conexión SQLAlchemy. |
| `COMMUNITY_NAME` | No (default `Comunidad`) | Nombre de la comunidad, mostrado en las pantallas de login, el panel de staff y la firma de los emails. Personaliza la instalación sin tocar código ni reconstruir el frontend — se sirve vía `GET /api/config`. |
| `APP_TIMEZONE` | No (default `Europe/Madrid`) | Zona horaria (IANA) usada para formatear fechas dentro del texto de los emails. |
| `SMTP_HOST` / `SMTP_PORT` / `SMTP_USER` / `SMTP_PASS` / `SMTP_FROM` / `SMTP_TLS` | No (default MailHog) | Configuración del servidor de correo. Ver [docs/EMAIL_Y_DESPLIEGUE.md](./docs/EMAIL_Y_DESPLIEGUE.md). |

### 10.3 Ejecución local — con Docker

```bash
git clone https://github.com/TU_USUARIO/fincaspro.git
cd fincaspro
docker-compose up --build
```

| Servicio | URL |
|---|---|
| Frontend | http://localhost:5173 |
| API + docs | http://localhost:8000/docs |
| MailHog | http://localhost:8025 |

### 10.4 Ejecución local — sin Docker

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python seed.py
uvicorn main:app --reload

# Frontend (otra terminal)
cd frontend
npm install
npm run dev
```

### 10.5 Producción

- Definir `ENVIRONMENT=production` y `SECRET_KEY` obligatoriamente.
- Cambiar `DATABASE_URL` a PostgreSQL.
- Ajustar `allow_origins` en `main.py` (CORS) al dominio real.
- Servir el frontend como build estático (`npm run build` → `frontend/dist`) detrás de un servidor como Nginx, en vez del servidor de desarrollo de Vite.
- Configurar un proveedor SMTP real (ver [docs/EMAIL_Y_DESPLIEGUE.md](./docs/EMAIL_Y_DESPLIEGUE.md)).

---

## 11. Roadmap

### Estado completado antes de producción

- [x] CI de backend en GitHub Actions.
- [x] CI de frontend en GitHub Actions.
- [x] Ruff: lint y formato.
- [x] MyPy y Pyright.
- [x] ESLint y build de producción del frontend.
- [x] Suite automatizada: 109 tests.
- [x] Cobertura: 87,56 %.
- [x] Normalización de finales de línea mediante `.gitattributes`.
- [x] Configuración de calidad centralizada en `pyproject.toml`.

### Siguiente fase: preparación para producción

- [ ] Docker de producción separado del entorno de desarrollo.
- [ ] Build multi-stage del frontend y servidor estático con Nginx.
- [ ] Healthchecks y configuración de servicios.
- [ ] Revisión de persistencia de base de datos y archivos subidos.
- [ ] CORS y variables de entorno específicas de producción.
- [ ] HTTPS / reverse proxy.
- [ ] Revisión final de secretos y configuración de despliegue.

### Mejoras funcionales y técnicas posteriores

- [ ] Migración de SQLite a PostgreSQL + Alembic con migraciones versionadas.
- [ ] Sistema de permisos por acción en lugar de roles fijos.
- [ ] Registro de auditoría (quién cambió qué y cuándo).
- [ ] Rate limiting y bloqueo tras intentos de login fallidos.
- [ ] Multi-comunidad (una instalación gestionando varias comunidades).
- [ ] Paginación en los listados de la API.
- [ ] Revisar y ampliar cobertura específica de routers nuevos conforme se incorporen funcionalidades.

### Funcionalidades pendientes conocidas

- **Pantalla de administración para crear cuentas de staff** — actualmente las cuentas de staff se crean mediante `seed.py` o acceso directo a la base de datos.
- **Mostrar el número de seguimiento (`tracking`) del paquete** en las interfaces correspondientes.
- **Revisar las notificaciones de tickets** para confirmar y completar su activación cuando corresponda.

---

## 12. Calidad de código, tests y CI/CD

### 13.1 Objetivo

El proyecto utiliza integración continua para evitar que cambios con errores de sintaxis, estilo, tipos, tests o compilación del frontend lleguen a las ramas principales.

El workflow está en `.github/workflows/ci.yml` y se ejecuta en `push` y `pull_request` hacia `main` y `develop`.

### 13.2 Pipeline de backend

El job de backend se ejecuta sobre Ubuntu con Python 3.12 y 3.13:

| Comprobación | Herramienta | Objetivo |
|---|---|---|
| Lint | Ruff | Detectar errores y problemas de estilo |
| Formato | Ruff format | Garantizar formato reproducible |
| Tipado | MyPy | Análisis estático de tipos |
| Tipado | Pyright | Segundo análisis estático, integrado también con Pylance/VS Code |
| Tests | Pytest | Verificar el comportamiento funcional |
| Cobertura | pytest-cov | Mantener una cobertura mínima del 80 % |

Las migraciones generadas de Alembic se excluyen de las comprobaciones de código donde corresponde.

### 13.3 Pipeline de frontend

El job de frontend utiliza Node.js 20:

| Comprobación | Herramienta | Objetivo |
|---|---|---|
| Instalación reproducible | `npm ci` | Instalar exactamente el lockfile |
| Lint | ESLint | Detectar errores y código problemático |
| Build | Vite | Comprobar que el bundle de producción se genera correctamente |

ESLint actualmente termina sin errores; pueden aparecer warnings de hooks no bloqueantes.

### 13.4 Resultado de la última verificación

El estado validado antes de continuar con producción es:

- **109/109 tests pasando**.
- **87,56 % de cobertura**.
- Ruff: limpio.
- MyPy: limpio.
- Pyright: limpio.
- ESLint: 0 errores.
- Build de producción del frontend: correcto.

La configuración de Ruff, MyPy, Pyright, pytest y coverage está centralizada en `pyproject.toml`. Se eliminó una configuración independiente de Pyright que podía provocar diferencias entre entornos.

### 13.5 Normalización del código entre sistemas

`.gitattributes` fuerza finales de línea LF. Esto evita que Windows (CRLF) y Linux/GitHub Actions (LF) generen cambios de formato artificiales y errores masivos del linter.

### 13.6 Ejecución local del mismo control de calidad

```bash
cd backend
ruff check .
ruff format --check .
mypy .
pyright .
pytest tests/ -v --cov=. --cov-report=term-missing --cov-fail-under=80

cd ../frontend
npm ci
npm run lint
npm run build
```

### 13.7 Cobertura y Codecov

El workflow genera `backend/coverage.xml` y puede subirlo a Codecov en la ejecución de Python 3.13. El token se configura como secret `CODECOV_TOKEN`.

La subida es opcional y no bloquea el CI si Codecov no está configurado.

---

## 13. Guía para desarrolladores

### 13.1 Convenciones de código

- **Backend:** un router por recurso, bajo `routers/`; un modelo por tabla, bajo `models/`; todos los schemas de entrada/salida centralizados en `schemas.py` (no repartidos por routers).
- **Nombres en español** para dominio de negocio (`vecino`, `piso`, `avisos`), en inglés para lo puramente técnico (`router`, `schema`, `token`) — se mantiene esa mezcla de forma consistente en todo el proyecto.
- **Imports siempre "planos"** dentro de `backend/` (`from database import ...`, no `from backend.database import ...`): el backend se ejecuta con `backend/` como raíz, no como paquete instalado.
- **Estados como strings, no enums:** `"pendiente"`/`"en_proceso"`/`"resuelto"`, `"true"`/`"false"` como texto en vez de booleano en algunos campos (`portal_activo`, `activo`, `notificado`). Es una decisión heredada del diseño original — al tocar estos campos, respetar el valor literal exacto (minúsculas, sin acentos) para no romper filtros del frontend.

### 13.2 Buenas prácticas específicas de este proyecto

- Cualquier endpoint que envíe email debe ser `async def` y usar `await` dentro de un `try/except` — nunca `asyncio.create_task()` desde un endpoint síncrono (ver [8.3](#83-lógica-de-negocio-relevante)).
- Antes de añadir un campo nuevo a un modelo, añadirlo también al schema Pydantic correspondiente (`schemas.py`) — un campo que solo existe en el modelo SQLAlchemy nunca llega a la API.
- Antes de dar por hecho que "ya está implementado" porque existe el endpoint y el método en `client.js`, comprobar que **hay una pantalla real que lo llama** — varias funcionalidades de este proyecto (registro de portal, reporte de avería del vecino) llegaron a tener el backend completo semanas antes de que existiera el formulario correspondiente.
- Todo endpoint nuevo debería llevar al menos un test en `backend/tests/` que cubra el camino feliz y un caso de error — la suite corre en cada push vía GitHub Actions.

### 13.3 Organización del código al añadir una funcionalidad nueva

1. **Modelo** (`models/`) — si hace falta una tabla o columna nueva.
2. **Schema** (`schemas.py`) — el contrato de entrada/salida.
3. **Router** (`routers/`) — el endpoint, con sus dependencias de autenticación/autorización.
4. **Registro en `main.py`** si es un router nuevo (`app.include_router(...)`).
5. **Cliente** (`frontend/src/api/client.js`) — un método que llame al endpoint.
6. **Pantalla/componente** (`frontend/src/App.jsx`) — la UI que realmente use ese método del cliente.
7. **Test** (`backend/tests/`) — al menos camino feliz + un caso de error.

Seguir este orden evita el patrón que se repitió varias veces en este proyecto: backend completo, pero sin pantalla que lo use.

---

# Actualización 1.1 — Docker producción y operación

## Estado de la arquitectura de despliegue

El proyecto dispone ahora de dos perfiles diferenciados:

### Desarrollo

- `docker-compose.yml`
- FastAPI con recarga automática.
- Vite dev server.
- MailHog.
- SQLite local.
- Código fuente montado como volumen.

### Producción

- `docker-compose.prod.yml`.
- Backend FastAPI sobre Python 3.13.
- Uvicorn sin `--reload`.
- Alembic para gestionar el esquema.
- Frontend React compilado con Vite.
- Nginx para servir los archivos estáticos y actuar como reverse proxy.
- Volúmenes persistentes para SQLite y uploads.
- Health checks.
- Configuración por variables de entorno.

## Flujo de producción

```text
Cliente
  │
  ▼
Nginx :80
  ├── /              → React compilado
  ├── /api/          → FastAPI :8000
  └── /uploads/      → FastAPI :8000
                         │
                         ▼
                    SQLite /data
```

## Migraciones

En producción `Base.metadata.create_all()` no crea tablas. El contenedor ejecuta:

```bash
alembic upgrade head
```

La migración `9aec2efa12cd` representa el esquema inicial actual y `f7d9063b8a35` añade `tickets.alcance`.

Esto evita depender de la creación automática de tablas al arrancar y permite evolucionar el esquema de forma controlada.

## Health checks

- Backend: `GET /health`.
- Nginx: `GET /nginx-health` interno.

Estos endpoints permiten a Docker detectar contenedores que no están respondiendo correctamente.

## Configuración de producción

La plantilla `.env.production.example` documenta las variables necesarias. El archivo real `.env.production` está excluido de Git y debe gestionarse fuera del repositorio.

Variables especialmente sensibles:

- `SECRET_KEY`
- `SMTP_PASS`
- `SMTP_USER`
- `DATABASE_URL` cuando incluya credenciales de un motor externo.

## CORS

`CORS_ORIGINS` permite declarar una lista separada por comas. En producción debe contener únicamente los orígenes públicos que realmente necesiten acceder a la API.

La aplicación utiliza el mismo origen para el frontend y la API cuando se sirve detrás de Nginx, por lo que el navegador normalmente no necesita CORS entre frontend y backend.

## Limitación actual del rate limiting

El rate limiting de `slowapi` utiliza almacenamiento en memoria. Por ese motivo el despliegue de producción utiliza un único worker de Uvicorn por defecto. Si en el futuro se escala horizontalmente, se deberá migrar el almacenamiento del rate limiter a un backend compartido (por ejemplo Redis) antes de considerar el escalado seguro.

## HTTPS

El compose de producción prepara HTTP y reverse proxy, pero no genera certificados TLS. HTTPS debe terminarse mediante un proxy/balanceador con certificados válidos o mediante una futura configuración Nginx + Let's Encrypt.

## Persistencia

Los volúmenes de producción son:

- `fincaspro_db`: `/data/fincaspro.db`.
- `fincaspro_uploads`: `/app/uploads`.

Los uploads deben incluirse en la estrategia de copias de seguridad junto con la base de datos.
