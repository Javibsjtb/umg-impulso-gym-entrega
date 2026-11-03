# Casos de prueba y aceptación

Ejecutar en entorno de pruebas con datos ficticios. No usar pagos reales. Registrar resultado, commit, fecha y ejecutor; no marcar manuales como aprobados sin ejecutarlos.

| Caso | Preparación / pasos | Resultado esperado | Automatización |
|---|---|---|---|
| CP-01 | Entrar con usuario/contraseña válidos y rol | Panel accesible; sesión creada | WebTests |
| CP-02 | Fallar cinco veces y reintentar antes de 15 min | Respuesta 429, sin acceso | WebTests |
| CP-03 | Recepción abre URL de anulación/reporte/usuarios y envía POST | 403; ninguna modificación | WebTests |
| CP-04 | Crear socio con mismo código, correo malo y teléfono inválido | Errores por campo; no guardar | BusinessTests / WebTests |
| CP-05 | Buscar socios y pasar a página 2 | Resultados y filtro conservado | WebTests |
| CP-06 | Crear plan de precio negativo o duración cero | Rechazado | BusinessTests |
| CP-07 | Contratar 30 días desde hoy | Fin = inicio + 29 días | BusinessTests |
| CP-08 | Inscribir otro período que toca el último día actual | Rechazado por superposición | BusinessTests |
| CP-09 | Renovar desde día siguiente al fin | Contrato programado válido | BusinessTests |
| CP-10 | Modificar precio/duración de plan existente | Contrato previo conserva valores | BusinessTests |
| CP-11 | Pagar Q50 a contrato de Q180 | Saldo Q130; acceso denegado | BusinessTests |
| CP-12 | Intentar monto 0, negativo o mayor que saldo | Rechazado sin movimiento | BusinessTests |
| CP-13 | Transferencia sin referencia | Rechazado | BusinessTests |
| CP-14 | Enviar dos veces el mismo token y datos de pago | Un solo comprobante | BusinessTests |
| CP-15 | Reutilizar token con datos distintos | Rechazado | BusinessTests |
| CP-16 | Completar pago y registrar asistencia | Acceso y registro aceptados | BusinessTests / WebTests |
| CP-17 | Repetir asistencia hoy | Conservar una sola fila | BusinessTests |
| CP-18 | Socio inactivo, contrato vencido, futuro o pendiente | Acceso denegado en cada caso | BusinessTests |
| CP-19 | Entrada en último día de contrato pagado | Aceptada | BusinessTests |
| CP-20 | Anular pago con motivo | Mantener pago, guardar actor/motivo, restaurar saldo | BusinessTests |
| CP-21 | Cancelar membresía pagada | Sin acceso, pagos conservados, no reembolso | BusinessTests |
| CP-22 | Eliminar socio con historial / sin historial | Protegido / eliminado y auditado | WebTests |
| CP-23 | Reporte por rango, incluir cobro anulado | Total excluye anulado; detalle lo identifica | WebTests |
| CP-24 | Exportar nombre iniciado con fórmula | CSV escapa fórmula | WebTests |
| CP-25 | Insertar texto con script en nombre | Mostrar texto escapado, no ejecutar | WebTests |
| CP-26 | POST sin token CSRF | 403 | WebTests |
| CP-27 | Abrir cierre con GET | 405, sesión conservada | WebTests |
| CP-28 | Usuario sin grupo consulta API | 403; anónimo redirigido al login | WebTests |
| CP-29 | Buscar por nombre en recepción y elegir resultado | Llenar código sin recargar | Revisión de navegador + WebTests API |
| CP-30 | Dos cobros simultáneos de Q100 a saldo Q180 | Solo uno aceptado | ConcurrencyTests, PostgreSQL |
| CP-31 | Dos entradas simultáneas | Una asistencia | ConcurrencyTests, PostgreSQL |
| CP-32 | Dos renovaciones simultáneas superpuestas | Solo una aceptada | ConcurrencyTests, PostgreSQL |
| CP-33 | Navegar en 390 px y escritorio | Controles legibles y menú operativo | Revisión visual |
| CP-34 | Imprimir comprobante | Sin sidebar ni botones, datos completos | Manual pendiente de impresora/PDF del equipo |
| CP-35 | Publicar y reiniciar servidor | Datos persisten, HTTPS y login operativos | Pendiente de despliegue |
| CP-36 | Restaurar respaldo en DB separada | Conteos y relaciones consistentes | Pendiente en proveedor |
| CP-37 | Prueba observada por gimnasio real | Criterios aceptados o incidencias anotadas | Pendiente de negocio |

## Datos y criterios para pruebas de carga pendientes

Dataset sintético de 1,000 socios, 3,000 contratos y cinco operadores concurrentes. Medir p50/p95, errores y consultas lentas de búsqueda, panel, cobro y asistencia. Objetivo propuesto p95 < 1 segundo; acordarlo con negocio y proveedor. No hay benchmark ejecutado en esta entrega.

## Registro manual

| Fecha real | Caso | Entorno / commit | Resultado obtenido | Evidencia | Ejecutor |
|---|---|---|---|---|---|
| [pendiente] | | | | | |

Resultados automáticos y de navegador realmente realizados: `VALIDACION.md`.
