# Despliegue realista · Render y Railway

**Estado: preparado, no publicado.** Existe un repositorio privado en GitHub. No se dispone de cuenta autenticada de proveedor, dominio ni aprobación de costos. No existe URL de producción verificada. El servidor local no cuenta como aplicación publicada.

## Opción principal: Render + PostgreSQL

Se incluye `render.yaml` con servicio web, PostgreSQL, WhiteNoise, Gunicorn, verificación de salud y migraciones previas. Usa planes de pago (`starter` y `basic-256mb`) para disponer de pre-deploy y base persistente. Revisar nombres, disponibilidad y tarifas que muestre Render antes de crear recursos; este documento no autoriza un cobro ni promete hosting gratuito.

1. Crear el repositorio compartido, ejecutar CI y revisar las pruebas PostgreSQL. Seguir CONTRIBUTING.md.
2. Abrir Render y conectar el repositorio mediante **New → Blueprint**. Revisar el `render.yaml` y costos antes de confirmar.
3. Configurar variables con el dominio asignado. No usar comodines:

```dotenv
DEBUG=False
DEMO_MODE=False
SECRET_KEY=<clave aleatoria de al menos 50 caracteres>
DATABASE_URL=<URL interna de PostgreSQL del proveedor>
ALLOWED_HOSTS=nombre-asignado.onrender.com
CSRF_TRUSTED_ORIGINS=https://nombre-asignado.onrender.com
TRUST_PROXY=True
GYM_NAME=<nombre validado con el gimnasio>
```

Generar una clave localmente con `python -c "import secrets; print(secrets.token_urlsafe(64))"` y pegarla solo en las variables privadas del proveedor. Render puede generarla con el blueprint. No guardarla en Git ni en capturas.

4. Verificar la versión de Python disponible (blueprint propuesto: 3.13.12). Mantener Python 3.13 para reproducir el entorno. Construcción: `bash scripts/build.sh`.
5. Pre-deploy: `python manage.py migrate --noinput`. Inicio: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --access-logfile - --error-logfile -`.
6. Esperar despliegue exitoso. Desde la consola privada del servicio ejecutar `python manage.py createsuperuser`. Guardar credenciales privadamente. Crear cuentas operativas individuales.
7. Abrir `https://DOMINIO/health/` y comprobar `{"status":"ok"}`. Ingresar, crear un socio ficticio autorizado para pruebas y completar inscripción/pago/asistencia.
8. Reiniciar o redesplegar y comprobar persistencia. Revisar HTTPS, errores de login/CSRF y recursos estáticos. Probar desde un teléfono usando otra red.
9. Registrar URL, commit desplegado, fecha, responsable, resultados y evidencia sin credenciales. Solo entonces marcar publicado.

El encabezado de proxy solo se confía cuando Render/Railway lo controla y sobrescribe. No activar TRUST_PROXY detrás de un proxy que acepte encabezados del cliente sin limpiarlos.

## Alternativa: Railway con Dockerfile

1. Importar repositorio y añadir PostgreSQL en el mismo proyecto.
2. Referenciar `DATABASE_URL` del servicio PostgreSQL mediante variables privadas de Railway. Generar `SECRET_KEY` y configurar las otras variables de arriba con el dominio Railway.
3. Usar el Dockerfile incluido; exponer el puerto indicado por `PORT`. Configurar `/health/` como verificación.
4. Ejecutar `python manage.py migrate --noinput` como comando previo al despliegue, una sola vez por versión. No iniciar varias instancias que migren simultáneamente.
5. Generar dominio HTTPS y configurar ALLOWED_HOSTS/CSRF_TRUSTED_ORIGINS. Crear superusuario y cuentas operativas desde una consola privada.
6. Repetir la verificación y persistencia de Render. Consultar costos y límites antes de contratar.

## SQLite y almacenamiento efímero

No desplegar `db.sqlite3` dentro del contenedor o disco efímero. La configuración exige PostgreSQL cuando DEBUG=False. En producción la demo está bloqueada. Si el docente necesita demostración pública, usar una instancia separada, datos ficticios, cuentas limitadas y acceso acordado; no activar DEBUG públicamente.

## CI/CD

`.github/workflows/tests.yml` ejecuta checks, migraciones pendientes, 54 tests contra PostgreSQL 16, estáticos y seguridad de configuración. La suite ya pasó en [GitHub Actions](https://github.com/Javibsjtb/umg-impulso-gym/actions/runs/38933107025). Proteger main con ese resultado obligatorio y revisión cuando el plan de GitHub lo permita. Configurar autodeploy solo de main aprobado. No afirmar CI exitoso basándose en que el archivo existe.

## Backups y recuperación

- Habilitar backups del proveedor según el plan y política acordada.
- Para respaldo manual, usar `pg_dump --format=custom` con credenciales de la instancia en un entorno privado y guardar fuera del repositorio, cifrado o en almacenamiento controlado. No poner contraseñas en el historial de comandos.
- Restaurar con `pg_restore` en una base NUEVA de ensayo. Verificar conteos de socios, membresías, pagos y asistencias, relaciones y un recorrido de lectura. No restaurar sobre producción sin un plan de mantenimiento.
- Registrar fecha, versión de DB, resultado y responsable. Los objetivos de recuperación deben acordarse con el negocio; aún no han sido medidos.
- Conservar migraciones y commit del despliegue. Ante error, analizar logs y compatibilidad del esquema antes de revertir código. Una reversión de código no deshace automáticamente una migración.

## Diagnóstico breve

| Síntoma | Revisar |
|---|---|
| 400 / DisallowedHost | ALLOWED_HOSTS con dominio exacto, sin protocolo |
| CSRF 403 | CSRF_TRUSTED_ORIGINS con https, proxy confiable, cookies y sesión |
| Bucle HTTPS | TRUST_PROXY y encabezado X-Forwarded-Proto del proveedor |
| CSS no carga | collectstatic, STATIC_ROOT y WhiteNoise; logs de build |
| DB no conecta | DATABASE_URL privada, disponibilidad y permisos de PostgreSQL |
| Demasiados intentos | Esperar ventana; limpieza operativa con cleanup_login_attempts |
| Datos desaparecen | Confirmar PostgreSQL persistente; no usar SQLite efímero |

Referencias oficiales consultadas: [Render Django](https://render.com/docs/deploy-django), [Render deploys y pre-deploy](https://render.com/docs/deploys), [Render Blueprints](https://render.com/docs/infrastructure-as-code), [Django checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/). La publicación y la cuenta del proveedor siguen pendientes.
