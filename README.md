# Impulso Gym · Proyecto final de Desarrollo Web

Aplicación full-stack para administrar socios, planes, membresías, pagos y asistencia. Django 5.2, templates HTML, CSS responsivo propio, JavaScript Fetch y PostgreSQL en producción. SQLite permite abrir la demo sin instalar un servidor de base de datos.

**Estado:** implementación local funcional con datos ficticios. El negocio real, la validación del PRD, la participación de cinco estudiantes, la actividad de los estudiantes en el tablero, la revisión colaborativa y la publicación web son pendientes reales. Este trabajo no garantiza una nota ni sustituye esas evidencias.

Repositorio público de entrega: [Javibsjtb/umg-impulso-gym-entrega](https://github.com/Javibsjtb/umg-impulso-gym-entrega). [Por qué el historial comienza en noviembre de 2026](docs/CAMBIO_REPOSITORIO.md).

![Portada basada en Figma](docs/evidencias/portada-desktop.png)

![Panel de demostración](docs/evidencias/panel-desktop.png)

## Inicio rápido

Requisitos: Python 3.13 y Git. Ejecutar desde la carpeta que contiene `manage.py`.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Windows PowerShell: crear el entorno con `py -3.13 -m venv .venv`, activarlo con `.venv\Scripts\Activate.ps1` y copiar el archivo con `Copy-Item .env.example .env`. Si la política de PowerShell impide activar, usar directamente `.venv\Scripts\python.exe` en lugar de `python`.

Abrir **http://127.0.0.1:8000/** para la portada y **/panel/** para la administración. La revisión en esta Mac está abierta en el puerto **8001** porque 8000 estaba ocupado. `seed_demo` imprime una contraseña aleatoria para `admin.demo` y `recepcion.demo`. Guardarla localmente. Volver a ejecutar el comando NO elimina datos ni restablece contraseñas. Para restablecer una cuenta local: `python manage.py changepassword admin.demo`.

La demo contiene 24 socios y tres planes, pagos ficticios, membresías vigentes, vencidas, futuras y con saldo pendiente. Las fechas son relativas al día en que se cargan. No contiene tarjetas ni personas reales. La cuenta administrativa demo NO es un superusuario de Django.

## Qué puedes hacer

- Panel con socios habilitados, ingresos del mes, asistencia diaria y vencimientos próximos.
- Crear, buscar por nombre completo, editar, desactivar y eliminar socios sin historial; paginación de 15 registros.
- Administrar planes; conservar precio y duración de cada contrato aunque el plan cambie.
- Inscribir y renovar membresías sin superposición de períodos.
- Registrar pagos parciales o completos con comprobante imprimible e idempotencia ante reenvíos.
- Anular cobros con motivo, fecha y responsable; no borrar movimientos financieros.
- Admitir socios únicamente con membresía vigente y pagada; una asistencia por día. Consultar el historial por fecha.
- Buscar socios sin recargar la página mediante `/api/socios/` y Fetch.
- Exportar pagos y asistencias a CSV por rango de fechas, filtrar y revisar auditoría.
- Crear usuarios de Administración y Recepción; cambiar la contraseña propia.

No procesa tarjetas, no emite facturas fiscales y no automatiza devoluciones bancarias.

## Verificar

```sh
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test gym --verbosity 2
python manage.py collectstatic --noinput
```

La suite tiene 56 pruebas. En SQLite se omiten tres que comprueban concurrencia mediante bloqueos de PostgreSQL. Resultado local documentado en [Validación](docs/VALIDACION.md). Las **54 pruebas pasaron en PostgreSQL 16 en [GitHub Actions](https://github.com/Javibsjtb/umg-impulso-gym/actions/runs/38933107025)**, sin omisiones.

### PostgreSQL local con Docker

```sh
docker compose up -d db
```

Configurar `DATABASE_URL=postgresql://impulso:local-development-only@127.0.0.1:54329/impulso` en `.env`, mantener `DEBUG=True`, y repetir migraciones y tests. La base estará vacía; ejecutar `seed_demo` solo si se quiere una demo aparte. El volumen de Docker conserva sus datos. No usar las credenciales de desarrollo en Internet.

## Arquitectura y organización

```text
config/                 Configuración, URLs y WSGI
gym/models.py           Modelo relacional y restricciones
gym/services.py         Operaciones transaccionales y reglas del negocio
gym/forms.py            Validaciones de entrada
gym/views.py            Controladores, permisos, reportes y API
static/gym/             CSS, JavaScript e icono, sin CDN
templates/              Interfaz Django en español
gym/tests.py            Pruebas funcionales, seguridad y concurrencia
gym/migrations/         Esquema versionado
.github/                CI, plantilla de PR e issues
docs/                   PRD, Scrum, DER, manuales y evidencias
```

El navegador envía formularios con CSRF; las vistas autorizan el rol y los servicios validan y guardan en una transacción. En PostgreSQL, `select_for_update()` serializa los cobros y accesos concurrentes. En SQLite esos bloqueos no tienen la misma garantía; se usa solo para desarrollo de un usuario.

## Documentación y entrega

- [Índice de documentos](docs/INDICE.md)
- [Nota sobre el cambio de repositorio](docs/CAMBIO_REPOSITORIO.md)
- [PRD en PDF solicitado por la rúbrica](docs/PRD_Impulso_Gym_UMG.pdf)
- [PRD editable y criterios de aceptación](docs/PRD.md)
- [Levantamiento del negocio real](docs/NEGOCIO_REAL.md)
- [Scrum, backlog y sprints](docs/SCRUM.md)
- [Diagrama entidad-relación y diccionario](docs/DER.md)
- [Casos de prueba](docs/CASOS_DE_PRUEBA.md)
- [Seguridad y decisiones técnicas](docs/ARQUITECTURA_SEGURIDAD.md)
- [Despliegue en Render / Railway](docs/DESPLIEGUE.md)
- [Manual de uso](docs/MANUAL_USUARIO.md)
- [Guía para exposición](docs/EXPOSICION.md)
- [Matriz de requisitos del PDF](docs/MATRIZ_UMG.md)
- [Pendientes de entrega](docs/PENDIENTES.md)
- [Contribución y Git](CONTRIBUTING.md)

## Producción

No subir `.env`, la base SQLite, contraseñas ni entrevistas privadas. Configurar `DEBUG=False`, clave aleatoria, dominio permitido, origen CSRF y PostgreSQL. Usar `gunicorn config.wsgi:application` y WhiteNoise. La configuración rechaza SQLite en producción. [Las instrucciones de despliegue](docs/DESPLIEGUE.md) explican los pasos y costos por confirmar.

Para una instalación real vacía, crear la cuenta de mantenimiento con `python manage.py createsuperuser`, ingresar al sistema y crear las cuentas operativas desde Equipo y roles. No cargar la demo en producción. El superusuario tiene acceso a todo y debe reservarse para mantenimiento.

## Estado académico

Esta versión fue integrada y publicada desde la Mac del titular `Javibsjtb`. Se usaron herramientas de IA para preparar el prototipo. El commit de publicación no demuestra desarrollo individual de cinco estudiantes. El negocio real, su aprobación, las contribuciones del equipo y el despliegue web siguen pendientes de evidencia verificable.
