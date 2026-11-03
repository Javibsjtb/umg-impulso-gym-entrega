# Manual de uso

## Ingresar

Abrir la URL configurada. Introducir la cuenta propia. Cinco fallos bloquean temporalmente el identificador; esperar la ventana de 15 minutos o contactar al administrador. Cerrar con el botón de la barra lateral. Cambiar contraseña desde el perfil inferior.

## Recorrido de recepción

1. En **Socios → Nuevo socio**, registrar código único, nombres y apellidos. Contacto opcional. Guardar.
2. En su ficha, elegir **Membresía**. Seleccionar un plan y fecha. El sistema calcula el final y rechaza superposición.
3. Registrar el pago. Se permite un abono que no supere el saldo. Transferencia/tarjeta requieren referencia del comprobante externo; el sistema no realiza el cargo.
4. Imprimir el comprobante interno si se necesita. No es una factura fiscal.
5. En **Asistencia**, escribir el código o buscar por nombre. Seleccionar resultado y pulsar **Validar y registrar**.
6. Si tiene saldo o no tiene vigencia, el mensaje explica el rechazo. Resolver desde la ficha; no crear entradas por fuera del sistema.
7. Para renovar, usar **Renovar**; la fecha sugerida comienza después del último período no cancelado o desde hoy si ya venció.

## Administración

- **Planes:** crear/editar. Desactivar los que ya no se ofrecen. No borrar planes usados.
- **Socios:** desactivar desde Editar ficha para impedir acceso y nuevas membresías. El historial se conserva.
- **Pagos:** abrir comprobante → Anular → motivo. Solo para corregir registros. El saldo vuelve a quedar pendiente y puede impedir entrada.
- **Membresías:** Cancelar con motivo. Pagos anteriores permanecen; un eventual reembolso se realiza fuera del sistema y debe conciliarse según el procedimiento del negocio.
- **Reportes:** elegir fechas → Consultar o Descargar CSV. El total usa pagos no anulados según su estado actual.
- **Equipo y roles:** crear cuentas individuales. Desactivar a quien ya no deba ingresar. No compartir contraseñas.
- **Historial:** consultar quién realizó operaciones y cuándo.

## Estados

| Estado | Significado |
|---|---|
| Vigente | Dentro del período y sin saldo pendiente |
| Por vencer | Dentro del período, pagada y termina en los siguientes 7 días |
| Pago pendiente | Dentro del período pero aún falta pagar |
| Programada | Inicia después de hoy |
| Vencida | Terminó antes de hoy |
| Cancelada | Administración la canceló explícitamente |

El estado activo/inactivo de la ficha es independiente del estado de membresía. Un socio inactivo no entra aunque su contrato aparezca vigente.

## Operación sin conexión

La aplicación requiere conexión con el servidor. Si el servicio está caído, usar un registro temporal aprobado por el negocio y conciliarlo al restablecerse. No introducir fechas falsas: la interfaz actual registra asistencia del día, no carga retroactiva. La política de contingencia debe acordarse antes de usarla realmente.
