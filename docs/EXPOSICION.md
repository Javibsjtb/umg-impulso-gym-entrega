# Guía de exposición · 12 minutos + preguntas

Guion propuesto para cinco integrantes. Sustituir nombres y completar la evidencia real. Se entrega como guía editable; no como presentación que afirme un negocio inexistente.

## Preparación

Confirmar URL HTTPS y prueba desde otro dispositivo; disponer de demo local como respaldo, nunca como sustituto silencioso del despliegue. Llevar PRD validado, DER, tablero real, repositorio compartido, PR y resultados de pruebas. No mostrar contraseñas ni datos personales. Usar demo ficticia durante la exposición.

## 0:00–2:00 · Integrante 1, necesidad y alcance

Mostrar nombre y descripción del gimnasio real, proceso observado y evidencia autorizada. Explicar **problema → necesidad → solución**, con una observación concreta. Presentar objetivo y límites. Mientras no haya levantamiento, decir expresamente: «Esta es una propuesta y un prototipo; falta validar el negocio». No presentar una entrevista inventada.

## 2:00–3:30 · Integrante 2, Scrum y colaboración

Mostrar tablero con las cinco columnas exigidas y una tarjeta real que enlace su issue, rama, PR y prueba. Explicar un bloqueo y cómo lo resolvieron, solo si ocurrió. Mostrar aportes propios de los cinco. Aclarar el papel de la IA en el código inicial.

## 3:30–6:00 · Integrante 3, experiencia y socios

Entrar como recepción. Mostrar vista móvil. Crear `EXPO-001` con nombre ficticio. Buscarlo por código y abrir ficha. Señalar validaciones; intentar código repetido. Explicar por qué una ficha con historial se desactiva en lugar de borrarse.

## 6:00–8:30 · Integrante 4, membresías y pagos

Crear contrato Esencial desde hoy (Q180 en la demo). Registrar Q50. Mostrar saldo Q130. Intentar entrada: debe rechazarse. Completar Q130, abrir comprobante y volver a registrar entrada: aceptada. Explicar que el cobro se registra, no se procesa por una pasarela. Mostrar cómo la renovación impide solapamientos.

## 8:30–10:00 · Integrante 5, controles y reportes

Repetir entrada: no duplica. Mostrar socio vencido. Entrar como administración, filtrar reporte y descargar CSV. Explicar motivo y conservación al anular un pago. Mostrar que recepción no accede a esas acciones.

## 10:00–12:00 · Arquitectura y cierre, participan todos

Mostrar DER y recorrido navegador → vista → servicio → PostgreSQL. Ejecutar un test representativo, enseñar CI real si existe y mostrar la URL desplegada. Explicar pendientes sin ocultarlos. Cada integrante presenta una decisión técnica de su aporte.

## Preguntas que todos deben poder responder

| Pregunta | Respuesta que deben comprender |
|---|---|
| ¿Por qué Django? | Integra autenticación, ORM, forms, migraciones y tests; es una opción autorizada por el PDF |
| ¿Por qué PostgreSQL? | Base relacional con persistencia y bloqueos de filas para cobros concurrentes |
| ¿Por qué SQLite local? | Reduce instalación para demo individual; no ofrece la misma garantía de concurrencia |
| ¿Qué evita un doble cobro? | Token único para reenvíos más validación de saldo dentro de transacción con bloqueo |
| ¿Qué pasa si cambia el precio? | Cada contrato conserva su precio y fechas, independientes del catálogo actual |
| ¿Por qué end_date = inicio + días − 1? | La fecha inicial y la final cuentan como días de acceso |
| ¿Dónde se revisa el rol? | En el servidor, no solo escondiendo botones |
| ¿Cómo se evita SQL injection? | Consultas parametrizadas por ORM, sin concatenar SQL |
| ¿Qué es CSRF? | Un token impide que otro sitio envíe formularios válidos aprovechando una sesión |
| ¿Anular es reembolsar? | No; corrige el registro y restaura saldo. No mueve dinero bancario |
| ¿Cómo recuperan una falla? | Logs, respaldo, restauración probada y despliegue de versión conocida |
| ¿Qué falta para decir terminado? | Negocio validado, equipo con evidencia real, PR/CI y despliegue verificado |

## Ensayo individual obligatorio

Cada integrante debe poder recrear el ambiente desde README, ubicar un modelo y su relación, explicar una regla de servicio, ejecutar un test, resolver un error de formulario y demostrar su PR. Si alguien no puede hacerlo, programar una sesión de revisión antes de presentar.
