# Validación técnica · 16 de octubre de 2026

## Ejecución local comprobada

- Python 3.13, Django 5.2.18 y SQLite.
- `python manage.py test gym --verbosity 1`: **54 pruebas descubiertas, 51 aprobadas y 3 omitidas**, sin fallos, 25.512 segundos. Las omitidas necesitan bloqueos de PostgreSQL.
- `python manage.py check`: sin incidencias.
- `python manage.py makemigrations --check --dry-run`: sin cambios pendientes.
- `python manage.py collectstatic --noinput`: completado, 162 archivos fuente estáticos, salidas comprimidas y con hash.
- `check --deploy --fail-level WARNING` con DEBUG=False, dominio concreto, clave de prueba larga y URL PostgreSQL: sin incidencias. Es un chequeo de configuración; no verifica una conexión a producción.

## Navegador

Portada y panel revisados a 1440 px y 390 px. Menú móvil abre/cierra; navegación a planes funciona; no hay desbordamiento horizontal global. Login real de la cuenta demo llega a `/panel/`. Las capturas corresponden a datos ficticios. La búsqueda y el acceso se comprueban también en la suite.

## PostgreSQL 16 en GitHub Actions

[Resultado real aprobado](https://github.com/Javibsjtb/umg-impulso-gym/actions/runs/38933107025), commit `0c8edcb`: **54 pruebas aprobadas, cero omitidas**, 38.019 segundos. También completó migraciones pendientes, recopilación de estáticos y comprobación de seguridad de producción. La primera ejecución detectó un supuesto incorrecto del test sobre el número del recibo y conexiones de workers sin cerrar; ambos se corrigieron en ese commit y se repitió la suite.

La revisión en navegador confirmó búsqueda Fetch, registro de la primera asistencia y rechazo de una repetida sin incrementar el contador; sin errores de consola. La galería fue ajustada para que el tamaño intrínseco de las fotos no amplíe las filas.

## Límites de esta evidencia

La base local SQLite no permite demostrar la protección ante escrituras concurrentes de PostgreSQL. Las tres pruebas específicas sí se ejecutaron satisfactoriamente en el CI enlazado arriba. Tampoco se ha comprobado un despliegue público, restauración de backup o aceptación por un negocio real.

Los casos manuales propuestos en CASOS_DE_PRUEBA.md no se deben marcar todos aprobados con base en este documento. El equipo debe ejecutar los que dependan de producción, accesibilidad asistida, aceptación o configuración real.
