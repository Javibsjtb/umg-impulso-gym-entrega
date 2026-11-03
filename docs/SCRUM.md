# Scrum y seguimiento real

## Estado actual

Existe un prototipo asistido por IA y commits locales reales bajo esa autoría. **Existe un [tablero privado de GitHub Projects](https://github.com/users/Javibsjtb/projects/1) con las cinco columnas y 15 issues creados realmente.** No existe todavía un equipo de cinco registrado, sprint celebrado ni PR de estudiantes. El [PR técnico inicial](https://github.com/Javibsjtb/umg-impulso-gym/pull/1) fue preparado con IA. El [tablero local](tablero.html) es una vista de preparación del backlog propuesto; no sustituye GitHub Projects/Trello ni un historial colaborativo real.

## Tablero compartido recomendado: GitHub Projects

El proyecto `UMG · Impulso Gym` ya contiene las columnas exactas:

**Product Backlog → Sprint Backlog → En progreso → Revisión/Testing → Finalizado**.

Añadir a los cinco integrantes. Cada tarjeta debe contener ID de historia, necesidad, criterio de aceptación, responsable, sprint, estimación, rama, PR, pruebas y evidencia. Registrar los cambios de estado cuando ocurran. No rellenar retroactivamente reuniones o fechas.

Las 15 historias de `backlog.csv` ya están publicadas como issues y añadidas al Project. Están en Product Backlog porque todavía necesitan validación y asignación real. El CSV es una propuesta, no un registro histórico. GitHub Projects debe conservar actividad real desde que el equipo comienza a usarlo.

## Backlog propuesto

| ID | Historia | Prioridad | Puntos propuestos | Sprint | Responsable propuesto |
|---|---|---|---|---|---|
| US-01 | Como PO quiero validar la necesidad con un gimnasio real | Must | 5 | 1 | Integrante 1 |
| US-02 | Como equipo quiero acordar PRD, roles y tablero | Must | 3 | 1 | Integrantes 1 y 2 |
| US-03 | Como operador quiero iniciar sesión según mi rol | Must | 3 | 1 | Integrante 2 |
| US-04 | Como recepcionista quiero registrar y buscar socios | Must | 5 | 1 | Integrante 3 |
| US-05 | Como administrador quiero configurar planes válidos | Must | 3 | 1 | Integrante 3 |
| US-06 | Como recepcionista quiero inscribir y renovar sin superponer períodos | Must | 5 | 2 | Integrante 4 |
| US-07 | Como recepcionista quiero cobrar sin exceder el saldo ni duplicar el pago | Must | 8 | 2 | Integrante 4 |
| US-08 | Como administrador quiero corregir cobros con evidencia | Must | 3 | 2 | Integrante 4 |
| US-09 | Como recepción quiero validar acceso y registrar asistencia | Must | 5 | 2 | Integrante 5 |
| US-10 | Como administración quiero anticipar vencimientos | Should | 3 | 2 | Integrante 1 |
| US-11 | Como administración quiero reportar ingresos y exportar CSV | Should | 3 | 3 | Integrante 5 |
| US-12 | Como usuario quiero utilizar el sistema en móvil | Must | 3 | 3 | Integrante 3 |
| US-13 | Como equipo quiero comprobar seguridad e integridad en PostgreSQL | Must | 5 | 3 | Integrantes 4 y 5 |
| US-14 | Como negocio quiero acceso HTTPS con respaldos y recuperación | Must | 5 | 3 | Integrante 2 |
| US-15 | Como equipo quiero validar aceptación y explicar el resultado | Must | 5 | 3 | Los cinco |

La funcionalidad inicial de varias historias ya existe en el prototipo. El trabajo del equipo consiste en revisarla, adaptarla a reglas reales, corregirla, validarla e integrarla con evidencia propia. Las estimaciones deben revisarse juntos; no equivalen a tiempo real ya trabajado.

## Sprints propuestos (fechas por acordar)

**Sprint 1, 1 semana:** negocio, PRD, tablero y evaluación técnica del prototipo; adaptación de autenticación, socios y planes. Entregable: alcance validado y primer recorrido probado. Dependencia: acceso al negocio.

**Sprint 2, 1 semana:** reglas de contratos, pagos, correcciones y asistencia; probar bordes y revisar código entre pares. Entregable: inscripción → pago → acceso con casos rechazados demostrables.

**Sprint 3, 1 semana:** reportes, móvil, PostgreSQL, CI, despliegue, recuperación y aceptación. Entregable: URL operativa, evidencias y exposición conjunta.

No son sprints ejecutados. Cambiar duración y fechas según el calendario del curso.

## Ceremonias y evidencias

- Planning: objetivo, capacidad, tareas seleccionadas y responsables. Acta real.
- Daily, 10 minutos: avance verificable, siguiente paso y bloqueo; anotar fecha y participantes.
- Revisión: mostrar funcionalidad al PO/negocio y registrar feedback.
- Retrospectiva: una mejora concreta, responsable y seguimiento en el siguiente sprint.

Usar `docs/evidencias/PLANTILLA_ACTA.md`. Mantener evidencia enlazada a la tarjeta; capturas sin información personal innecesaria.

## Definition of Ready

Necesidad entendida, criterio verificable, prioridad, dependencia conocida, responsable y estimación acordados.

## Definition of Done

Código revisado por otro integrante; pruebas relevantes pasan; validaciones y permisos comprobados; UI móvil revisada cuando aplique; documentación actualizada; PR integrado por el equipo; evidencia enlazada; PO acepta el criterio. Para entrega final también URL HTTPS funcional, DB persistente y negocio validado.

## Métricas honestas

Medir tareas terminadas, bloqueos, resultados de pruebas y tiempo de ciclo desde los movimientos reales del tablero. No generar burndown ni velocidad con valores inventados. El gráfico de asistencias de la aplicación utiliza datos demo del gimnasio y NO es una métrica Scrum.
