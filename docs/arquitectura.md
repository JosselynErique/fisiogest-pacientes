# Arquitectura de FisioGest

## 1. Decisión: de MVC a hexagonal + vertical slicing

En la Unidad 2 se propuso **MVC** con los patrones **Singleton** y **DAO**. Al implementar el sistema
completo se evolucionó a una **arquitectura hexagonal (puertos y adaptadores) organizada en slices
verticales**, sin perder lo diseñado:

| Diseño U2 | Implementación final | Dónde |
|---|---|---|
| Modelo | Entidades de dominio con sus reglas (`Paciente`, `Cita`, `Terapia`, `Usuario`) | `*/domain/*.py` |
| Controlador | Casos de uso (uno por funcionalidad) + endpoints Flask delgados | `*/features/*/caso_uso.py`, `endpoint.py` |
| Vista | Plantillas Jinja dentro de cada slice | `*/features/*/templates/` |
| DAO | Adaptadores SQLite que implementan los puertos (`PacienteRepository`…) | `*/adapters/sqlite_*.py` |
| Singleton | `Database`: una instancia por archivo de base de datos | `shared/infrastructure/database.py` |

**Por qué el cambio:** con 10 RF y 3 roles, un MVC por capas mezclaba reglas de negocio con Flask y
SQL. La arquitectura hexagonal deja el núcleo independiente y verificable sin base de datos (las pruebas
unitarias usan repositorios en memoria). El *vertical slicing* agrupa por funcionalidad, así que un
RF vive en una carpeta y agregar uno nuevo no obliga a tocar capas globales.

## 2. Vista de componentes

```mermaid
flowchart TB
    subgraph web["Adaptador de entrada · Flask"]
        direction LR
        E1[registrar_paciente/endpoint.py]
        E2[agendar_cita/endpoint.py]
        E3[registrar_terapia/endpoint.py]
        E4[...]
    end
    subgraph nucleo["Núcleo de la aplicación"]
        direction LR
        U1[RegistrarPaciente]
        U2[AgendarCita]
        U3[RegistrarTerapia]
        D[(Entidades y reglas<br/>Paciente · Cita · Terapia · Usuario)]
        P{{Puertos<br/>PacienteRepository · CitaRepository<br/>TerapiaRepository · UsuarioRepository<br/>PasswordHasher · ReporteQuery}}
    end
    subgraph infra["Adaptadores de salida"]
        direction LR
        S1[SqlitePacienteRepository]
        S2[SqliteCitaRepository]
        S3[SqliteTerapiaRepository]
        S4[WerkzeugPasswordHasher]
        DB[(SQLite)]
    end
    E1 --> U1
    E2 --> U2
    E3 --> U3
    U1 & U2 & U3 --> D
    U1 & U2 & U3 --> P
    S1 & S2 & S3 & S4 -. implementan .-> P
    S1 & S2 & S3 --> DB
    C[container.py<br/>raíz de composición] --> S1 & S2 & S3 & S4
```

Reglas que se verifican en `tests/unit/test_arquitectura.py`:

1. `domain/` y `caso_uso.py` **no importan** Flask, werkzeug, sqlite3 ni adaptadores.
2. Los adaptadores solo se instancian en `container.py`.
3. Cada slice tiene su `endpoint.py`.

## 3. Diagrama de clases del dominio

```mermaid
classDiagram
    class Usuario {
        +int id
        +str username
        +str nombre_completo
        +Rol rol
        +str password_hash
        +bool activo
        +int intentos_fallidos
        +datetime bloqueado_hasta
        +esta_bloqueado(ahora) bool
        +registrar_intento_fallido(ahora)
        +registrar_ingreso_exitoso()
    }
    class Rol {
        <<enumeration>>
        ADMINISTRADOR
        RECEPCIONISTA
        FISIOTERAPEUTA
    }
    class Paciente {
        +int id
        +str cedula
        +str nombres
        +str apellidos
        +date fecha_nacimiento
        +str telefono
        +str correo
        +str direccion
        +str contacto_emergencia
        +bool activo
        +crear(datos)$ Paciente
        +actualizar(datos)
        +dar_de_baja()
        +reactivar()
        +edad() int
    }
    class Cita {
        +int id
        +date fecha
        +time hora_inicio
        +time hora_fin
        +str motivo
        +EstadoCita estado
        +str motivo_cancelacion
        +programar(datos, ahora)$ Cita
        +se_solapa_con(otra) bool
        +cancelar(motivo)
        +marcar_atendida()
    }
    class EstadoCita {
        <<enumeration>>
        PROGRAMADA
        ATENDIDA
        CANCELADA
    }
    class Terapia {
        +int id
        +date fecha
        +str tipo
        +str zona_tratada
        +int dolor_inicial
        +int dolor_final
        +str procedimiento
        +str observaciones
        +registrar(datos, ...)$ Terapia
        +mejora_dolor() int
    }
    class HistorialClinico {
        +proximas_citas()
        +total_sesiones() int
        +evolucion_dolor() tuple
    }
    class Reporte {
        +Periodo periodo
        +int pacientes_atendidos
        +int sesiones
        +dict citas_por_estado
        +tasa_cancelacion() float
    }
    Usuario --> Rol
    Cita --> EstadoCita
    Paciente "1" --> "*" Cita : agenda
    Usuario "1" --> "*" Cita : atiende (fisioterapeuta)
    Paciente "1" --> "*" Terapia : recibe
    Usuario "1" --> "*" Terapia : registra
    Cita "1" --> "0..1" Terapia : genera
    HistorialClinico o-- Paciente
    HistorialClinico o-- Cita
    HistorialClinico o-- Terapia
```

## 4. Casos de uso por actor

```mermaid
flowchart LR
    A((Administrador))
    R((Recepcionista))
    F((Fisioterapeuta))
    subgraph FisioGest
        UC9([RF-09 Iniciar sesión])
        UCU([Gestionar usuarios])
        UC1([RF-01 Registrar paciente])
        UC2([RF-02 Modificar paciente])
        UC3([RF-03 Dar de baja paciente])
        UC4([RF-04 Agendar cita])
        UC5([RF-05 Validar cruce de horario])
        UC10([RF-10 Cancelar cita])
        UCA([Consultar agenda])
        UC6([RF-06 Registrar terapia])
        UC7([RF-07 Consultar historial])
        UC8([RF-08 Generar reportes])
    end
    A --- UC9 & UCU & UC8 & UC7
    R --- UC9 & UC1 & UC2 & UC3 & UC4 & UC10 & UCA & UC7
    F --- UC9 & UCA & UC6 & UC7
    UC4 -. include .-> UC5
```

## 5. Secuencia: agendar una cita (RF-04 / RF-05)

```mermaid
sequenceDiagram
    actor Recepcionista
    participant EP as agendar_cita/endpoint.py
    participant UC as AgendarCita
    participant C as Cita (dominio)
    participant PR as PacienteRepository
    participant UR as UsuarioRepository
    participant CR as CitaRepository
    Recepcionista->>EP: POST /citas/nueva
    EP->>UC: ejecutar(DatosCita)
    UC->>C: programar(datos, ahora)
    C-->>UC: Cita válida (horario 07:00-20:00, no domingo, no pasado)
    UC->>PR: obtener(paciente_id)
    UC->>UR: obtener(fisioterapeuta_id)
    UC->>CR: activas_del_fisioterapeuta(fecha)
    loop cada cita existente
        UC->>C: se_solapa_con(existente)
    end
    alt hay cruce
        UC-->>EP: ConflictError
        EP-->>Recepcionista: 409 + mensaje en el formulario
    else horario libre
        UC->>CR: guardar(cita)
        EP-->>Recepcionista: 302 → agenda del día
    end
```

## 6. Modelo de datos

```mermaid
erDiagram
    USUARIOS ||--o{ CITAS : "atiende"
    PACIENTES ||--o{ CITAS : "tiene"
    PACIENTES ||--o{ TERAPIAS : "recibe"
    USUARIOS ||--o{ TERAPIAS : "registra"
    CITAS ||--o| TERAPIAS : "genera"
    USUARIOS {
        int id PK
        text username UK
        text rol
        text password_hash
        int activo
    }
    PACIENTES {
        int id PK
        text cedula UK
        text nombres
        text apellidos
        int activo
    }
    CITAS {
        int id PK
        int paciente_id FK
        int fisioterapeuta_id FK
        text fecha
        text hora_inicio
        text hora_fin
        text estado
    }
    TERAPIAS {
        int id PK
        int paciente_id FK
        int fisioterapeuta_id FK
        int cita_id FK,UK
        text tipo
        int dolor_inicial
        int dolor_final
    }
```

## 7. Seguridad (RNF-02)

- Contraseñas con hash y sal (`werkzeug.security`, scrypt/pbkdf2); nunca se guardan en texto plano.
- Bloqueo temporal de 10 minutos tras 5 intentos fallidos; mensaje genérico que no revela si el
  usuario existe.
- Token CSRF en todos los formularios; cookies de sesión `HttpOnly` y `SameSite=Lax`.
- Cabeceras `Content-Security-Policy`, `X-Frame-Options: DENY`, `X-Content-Type-Options`.
- Autorización por rol en cada endpoint (`@requiere_rol`), validada con pruebas de integración.
- Protección contra redirecciones abiertas en el parámetro `next` del login.
