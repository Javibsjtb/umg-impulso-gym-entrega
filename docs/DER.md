# Modelo relacional · Diagrama Entidad-Relación

```mermaid
erDiagram
    USER ||--o{ USER_GROUP : pertenece
    GROUP ||--o{ USER_GROUP : agrupa
    MEMBER ||--o{ MEMBERSHIP : contrata
    PLAN ||--o{ MEMBERSHIP : define
    MEMBERSHIP ||--o{ PAYMENT : recibe
    MEMBER ||--o{ ATTENDANCE : registra
    MEMBERSHIP ||--o{ ATTENDANCE : habilita
    USER ||--o{ MEMBERSHIP : crea
    USER ||--o{ PAYMENT : registra
    USER o|--o{ PAYMENT : anula
    USER ||--o{ ATTENDANCE : registra
    USER ||--o{ AUDIT_EVENT : realiza
    MEMBER {
        bigint id PK
        varchar code UK
        varchar first_name
        varchar last_name
        varchar email
        varchar phone
        boolean active
        datetime created_at
    }
    PLAN {
        bigint id PK
        varchar name UK
        integer duration_days
        decimal price
        varchar description
        boolean active
    }
    MEMBERSHIP {
        bigint id PK
        bigint member_id FK
        bigint plan_id FK
        date start_date
        date end_date
        decimal price
        boolean cancelled
        varchar cancellation_reason
        bigint created_by_id FK
        datetime created_at
    }
    PAYMENT {
        bigint id PK
        bigint membership_id FK
        decimal amount
        varchar method
        varchar reference
        uuid token UK
        datetime created_at
        bigint created_by_id FK
        boolean voided
        varchar void_reason
        datetime voided_at
        bigint voided_by_id FK
    }
    ATTENDANCE {
        bigint id PK
        bigint member_id FK
        bigint membership_id FK
        date date
        datetime checked_in_at
        bigint created_by_id FK
    }
    AUDIT_EVENT {
        bigint id PK
        bigint actor_id FK
        varchar action
        varchar entity
        bigint entity_id
        varchar detail
        datetime created_at
    }
    LOGIN_THROTTLE {
        bigint id PK
        varchar key UK
        integer attempts
        datetime window_start
    }
    USER {
        integer id PK
        varchar username UK
        varchar password_hash
        boolean is_active
    }
    GROUP {
        integer id PK
        varchar name UK
    }
    USER_GROUP {
        bigint id PK
        integer user_id FK
        integer group_id FK
    }
```

El diagrama usa nombres conceptuales. Tablas físicas principales: `gym_member`, `gym_plan`, `gym_membership`, `gym_payment`, `gym_attendance`, `gym_auditevent`, `gym_loginthrottle`. `USER`, `GROUP`, `USER_GROUP` corresponden a `auth_user`, `auth_group` y `auth_user_groups`; Django incluye además permisos, sesiones y migraciones. El campo físico de contraseña se llama `password` y contiene el hash, nunca la contraseña en texto.

## Diccionario y decisiones

| Entidad | Finalidad / campos relevantes | Integridad |
|---|---|---|
| Socio | Código de recepción, nombre, contacto opcional, estado | Código único; datos mínimos; desactivación conserva historial |
| Plan | Nombre, días, precio decimal, descripción | Precio > 0; 1–366 días; nombre único |
| Membresía | Contrato fechado de un socio con un plan | FK protegidas; fin ≥ inicio; precio > 0; no superposición desde servicios |
| Pago | Movimiento asociado a un contrato | Monto > 0; token único; medio en catálogo; anulaciones conservadas |
| Asistencia | Entrada de un socio habilitada por contrato | UNIQUE(socio, fecha); relación socio/membresía comprobada por servicio |
| Auditoría | Autor, acción, tipo e ID de entidad | No usa FK genérica al objeto para conservar eventos de eliminaciones permitidas |
| Intento de acceso | HMAC del usuario, contador y ventana | No guarda la contraseña ni el nombre en texto; clave única |

Montos `Decimal(10,2)`, no flotantes. El precio de la membresía es una copia deliberada del precio aceptado. La fecha de fin también queda congelada al contratar. El saldo se calcula como precio menos pagos no anulados; no se mantiene un segundo saldo susceptible de desincronizarse.

## Cardinalidades y conservación

Un socio tiene muchas membresías; una membresía un solo plan y varios pagos/asistencias. Cada pago tiene un creador y puede tener un anulador. FK operativas usan `PROTECT`: nunca eliminar historial en cascada. La eliminación física se ofrece solo para socios/planes sin relaciones. Usuarios se desactivan.

El servicio de asistencia siempre selecciona la membresía del mismo socio; no permite inyectar una relación ajena mediante formulario. Las garantías entre varias filas (saldo y superposición) requieren los servicios y PostgreSQL. SQL directo o scripts que eludan los servicios quedan fuera de esas garantías.

## Migraciones

`gym/migrations/0001_initial.py` crea el esquema y las restricciones. Ejecutar `python manage.py migrate`. No editar una migración aplicada en producción; crear una nueva y revisar el cambio con el equipo.
