# PRD · Impulso Gym

Versión 0.1 · Propuesta de prototipo · **Pendiente de validación con negocio real y docente**.

## 1. Identificación y contexto

Nombre del sistema: Impulso Gym. Es una marca provisional de demostración, no un gimnasio identificado ni un cliente entrevistado. Curso: Desarrollo Web, Ingeniería en Sistemas, UMG. Equipo: cinco estudiantes pendientes de registrar en `EQUIPO.md`.

Negocio real: **[nombre legal/comercial, ubicación, responsable y actividad por completar]**. Dimensión: **[socios activos, personal de recepción, horarios, planes y volumen de movimientos por levantar]**.

## 2. Problema y necesidad

Hipótesis por validar: un gimnasio que registra membresías y cobros en papel u hojas separadas podría tener dificultad para confirmar vigencias, detectar saldos y consultar asistencias. No se afirma que un negocio real tenga este problema. Se requiere observar su proceso actual y obtener evidencia con consentimiento.

Cadena propuesta: registro fragmentado → necesidad de consulta confiable en recepción → aplicación que relaciona socio, plan, período, cobro y entrada.

## 3. Objetivo

Centralizar la operación para permitir que recepción confirme si un socio tiene acceso, registre pagos y consulte vencimientos desde una computadora o teléfono. Objetivo medible propuesto: resolver una consulta de acceso en menos de 30 segundos con datos previamente registrados, y evitar cobros por encima del saldo. Medir línea base y resultado en una prueba con el negocio; no se declara una mejora ya obtenida.

## 4. Usuarios y responsabilidades

| Usuario | Necesidad | Permisos |
|---|---|---|
| Administración | Configurar, supervisar y corregir | Operación completa, planes, anulaciones, cancelaciones, usuarios, reportes y auditoría |
| Recepción | Inscribir, cobrar y registrar entradas | Socios, membresías, cobros, comprobantes, consulta de planes, asistencia y panel |
| Mantenimiento | Recuperar/configurar la instalación | Superusuario Django; no cuenta compartida de uso diario |
| Socio | Ser atendido | No inicia sesión en esta versión |

## 5. Alcance

Una sola sede, moneda GTQ, zona horaria de Guatemala. Registro de socios sin datos médicos ni documentos de identidad; planes por días; membresías con precio fijo contratado; pagos manuales y comprobante interno; consulta de vigencia; asistencia diaria; administración de accesos y reportes operativos.

### Fuera de alcance

Facturación SAT/FEL, cargos automáticos, pasarela de pagos, transferencias reales, devolución bancaria, contabilidad formal, múltiples sedes, aplicación móvil nativa, torniquetes/biometría, QR de autoservicio, rutinas médicas, control de lesiones, venta de productos, clases con cupos, notificaciones automáticas y portal de socios.

## 6. Requerimientos funcionales y aceptación

| ID | Requisito | Criterio verificable |
|---|---|---|
| RF-01 | Autenticación y cierre seguro | Cuenta activa puede ingresar; cuenta sin rol recibe 403 en operación; logout exige POST; cinco fallos bloquean intentos por usuario durante la ventana de 15 minutos |
| RF-02 | Autorización | Recepción recibe 403 al invocar directamente edición de planes, usuarios, anulaciones, cancelaciones, reportes y auditoría |
| RF-03 | Gestión de socios | Código único, nombre obligatorio y contacto válido; ficha editable; baja lógica conserva historial; eliminación física solo sin relaciones |
| RF-04 | Gestión de planes | Precio positivo y duración de 1–366 días; desactivar impide nuevas inscripciones; editar no cambia contratos existentes |
| RF-05 | Membresías y renovaciones | Inicio más duración menos un día determina vencimiento inclusivo; períodos no se superponen; renovación sugerida después del último vencimiento |
| RF-06 | Registro de pagos | Monto positivo que no exceda saldo; transferencia/tarjeta requiere referencia; reenvío del mismo token y datos produce un solo comprobante |
| RF-07 | Correcciones con trazabilidad | Administración anula pago o cancela membresía con motivo; original se conserva; anular recalcula saldo; cancelar no hace reembolsos |
| RF-08 | Asistencia | Solo socio activo con período vigente y saldo cero; un registro al día; repetición informa sin duplicar; último día incluido |
| RF-09 | Panel y vencimientos | Indicadores calculados desde DB; próximos siete días filtrables; distinguir membresía vigente, por vencer, vencida, programada, pendiente o cancelada |
| RF-10 | Búsqueda y paginación | Socios por nombre/código/correo; membresías por socio; pagos por socio/referencia; 15 filas por página y filtros conservados |
| RF-11 | Consulta Fetch | Búsqueda desde 2 caracteres devuelve hasta 8 coincidencias autorizadas, sin correo/teléfono; selección llena el código sin recargar |
| RF-12 | Reportes | Filtro de fechas inclusivas; CSV de pagos incluye estado; total excluye anulados; datos que parecen fórmula se escapan |
| RF-13 | Cuentas individuales | Administrador crea recepción/administración; no puede quitarse su propio rol ni desactivarse; contraseñas se almacenan mediante hash de Django |
| RF-14 | Auditoría | Acciones operativas guardan usuario, acción, entidad, fecha y detalle; interfaz solo lectura |

## 7. Requerimientos no funcionales

| ID | Requisito / objetivo | Verificación |
|---|---|---|
| RNF-01 | Interfaz adaptable a 390 px y escritorio | Revisión visual y navegación real; tablas con scroll interno, sin desbordamiento global |
| RNF-02 | Integridad relacional | FK PROTECT, restricciones CHECK y UNIQUE, transacciones y bloqueos en PostgreSQL |
| RNF-03 | Seguridad | CSRF, escape HTML, ORM parametrizado, sesiones, control por rol, cabeceras y HTTPS de producción |
| RNF-04 | Rendimiento objetivo | Respuesta p95 menor de 1 s en consultas comunes para 1,000 socios y 5 operadores; medir en servidor final. No medido aún |
| RNF-05 | Reproducibilidad | Entorno aislado, dependencias fijadas, migraciones, variables documentadas y demo idempotente |
| RNF-06 | Disponibilidad | Aplicación accesible desde Internet con HTTPS, base persistente y backups; validación pendiente en proveedor |
| RNF-07 | Mantenibilidad | Capas separadas, pruebas de negocio/permisos y CI contra PostgreSQL |
| RNF-08 | Usabilidad | Campos etiquetados, navegación por teclado, foco visible, mensajes comprensibles y moneda/fechas consistentes |

## 8. Reglas que debe confirmar el negocio

1. El acceso requiere pago completo, sin días de gracia.
2. Un socio registra una asistencia por día; no se contabilizan reingresos.
3. Un plan dura días fijos, no meses calendario.
4. La membresía puede renovarse antes de vencer, iniciando después del período previo.
5. Los pagos parciales se permiten; habilitan acceso al completar el saldo.
6. No se permiten membresías simultáneas del mismo socio.
7. La anulación corrige un asiento; una devolución real se gestiona fuera del sistema.
8. La baja de un socio conserva historial. La política de retención de datos debe acordarse.

## 9. Riesgos y dependencias

Negocio no identificado; PRD del curso aún no proporcionado; reglas de gracia y calendarios por acordar; participación de cinco estudiantes sin evidencia; cuenta de hosting y GitHub aún no configuradas; costo de producción por aprobar; pruebas de carga, restauración y PostgreSQL por ejecutar en entorno final.

## 10. Aprobación real

Responsable del negocio: [pendiente] · fecha: [pendiente] · versión: [pendiente] · observaciones: [pendiente]. Product Owner: [pendiente]. Docente: [si aplica]. No completar firmas ni fechas hasta tener aprobación verificable.

El prototipo inicial se preparó antes de esta validación. No debe presentarse como si el PRD hubiera sido aprobado antes del desarrollo. El equipo debe validar el levantamiento y ajustar el alcance antes de iniciar sus iteraciones reales.
