# Email y despliegue

## Configuración de email

FincasPro dispone de un servicio de email basado en `aiosmtplib`. En desarrollo se utiliza MailHog para capturar los mensajes sin enviarlos a destinatarios reales.

Las notificaciones actualmente integradas deben documentarse según el estado real de los routers y servicios del proyecto. Antes de activar nuevas notificaciones en producción, conviene comprobar su flujo completo con tests y un proveedor SMTP real.

## Desarrollo local: MailHog

`docker-compose.yml` incluye MailHog como servidor SMTP de pruebas.

- SMTP: `localhost:1025`
- Interfaz web: `http://localhost:8025`

MailHog permite comprobar el contenido de los mensajes sin que salgan de la máquina de desarrollo.

## Configuración mediante variables de entorno

La configuración se realiza mediante las variables del backend:

```env
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USER=
SMTP_PASS=
SMTP_FROM=noreply@example.com
SMTP_TLS=false
```

En producción se sustituye MailHog por un proveedor SMTP real y nunca se deben guardar credenciales directamente en el código ni subirlas al repositorio.

## Producción

La configuración definitiva de producción se realizará en la siguiente fase del proyecto. Como mínimo deberá contemplar:

- Proveedor SMTP real.
- Credenciales almacenadas como variables de entorno o secrets.
- `ENVIRONMENT=production`.
- `SECRET_KEY` fuerte y privada.
- Dominio y configuración CORS revisados.
- HTTPS.
- Reverse proxy (Nginx u otra solución equivalente).
- Persistencia de base de datos y archivos subidos.
- Logs y healthchecks.

No se debe reutilizar MailHog en producción.

## Docker actual

El `docker-compose.yml` incluido actualmente está orientado al desarrollo local y proporciona el backend, frontend y MailHog.

Comandos habituales:

```bash
docker-compose up --build
docker-compose up -d
docker-compose logs -f backend
docker-compose down
docker-compose down -v
```

La variante específica para producción se implementará y documentará durante el paso 9.

## Base de datos y archivos

En desarrollo se utiliza SQLite. La aplicación está preparada para evolucionar hacia PostgreSQL mediante `DATABASE_URL`, pero la migración definitiva y el uso de Alembic forman parte de una fase posterior.

Las fotos de tickets se almacenan actualmente en el sistema de archivos. Antes de un despliegue productivo debe definirse una estrategia de persistencia adecuada para esos archivos.

## Escalabilidad

Para una instalación pequeña, SQLite puede ser suficiente. Para un entorno productivo con mayor concurrencia se recomienda PostgreSQL y un almacenamiento persistente para archivos.

La decisión definitiva de infraestructura se tomará durante la preparación de Docker producción.

## Docker producción — estado actual

La producción utiliza `docker-compose.prod.yml` y no reutiliza el servidor de desarrollo de Vite.

### Servicios

- `backend`: FastAPI + Uvicorn sobre Python 3.13.
- `frontend`: React compilado y servido por Nginx.

MailHog pertenece exclusivamente al entorno de desarrollo y no se inicia en producción.

### Arranque

```bash
cp .env.production.example .env.production
# Completar SECRET_KEY, SMTP y el resto de valores.

docker compose --env-file .env.production -f docker-compose.prod.yml up -d --build
```

El backend ejecuta las migraciones Alembic antes de arrancar Uvicorn. Si una migración falla, el contenedor no se considera correctamente iniciado.

### Email

En producción se deben utilizar credenciales SMTP reales y seguras. No deben introducirse contraseñas en `docker-compose.prod.yml`, Dockerfiles, GitHub Actions ni en el código fuente.

Para servicios que requieren autenticación moderna, utilizar la credencial o contraseña de aplicación recomendada por el proveedor.

### Base de datos

El despliegue actual mantiene SQLite para no introducir todavía un cambio de motor. El archivo se almacena en un volumen Docker persistente y Alembic controla su esquema.

La migración futura a PostgreSQL se considera una mejora independiente y deberá incluir una estrategia de migración y copia de seguridad.

### HTTPS

El compose actual no termina TLS. Antes de exponer la aplicación directamente a Internet debe existir una capa HTTPS válida delante de Nginx.
