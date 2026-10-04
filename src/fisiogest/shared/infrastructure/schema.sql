-- Esquema de FisioGest (SQLite). Es idempotente: puede ejecutarse en cada arranque.

CREATE TABLE IF NOT EXISTS usuarios (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    username          TEXT    NOT NULL UNIQUE,
    nombre_completo   TEXT    NOT NULL,
    rol               TEXT    NOT NULL CHECK (rol IN ('administrador', 'recepcionista', 'fisioterapeuta')),
    password_hash     TEXT    NOT NULL,
    activo            INTEGER NOT NULL DEFAULT 1,
    intentos_fallidos INTEGER NOT NULL DEFAULT 0,
    bloqueado_hasta   TEXT,
    creado_en         TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS pacientes (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    cedula              TEXT    NOT NULL UNIQUE,
    nombres             TEXT    NOT NULL,
    apellidos           TEXT    NOT NULL,
    fecha_nacimiento    TEXT,
    telefono            TEXT    NOT NULL DEFAULT '',
    correo              TEXT    NOT NULL DEFAULT '',
    direccion           TEXT    NOT NULL DEFAULT '',
    contacto_emergencia TEXT    NOT NULL DEFAULT '',
    activo              INTEGER NOT NULL DEFAULT 1,
    creado_en           TEXT    NOT NULL,
    actualizado_en      TEXT
);

CREATE TABLE IF NOT EXISTS citas (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    paciente_id        INTEGER NOT NULL REFERENCES pacientes (id),
    fisioterapeuta_id  INTEGER NOT NULL REFERENCES usuarios (id),
    fecha              TEXT    NOT NULL,
    hora_inicio        TEXT    NOT NULL,
    hora_fin           TEXT    NOT NULL,
    motivo             TEXT    NOT NULL DEFAULT '',
    estado             TEXT    NOT NULL DEFAULT 'programada'
                               CHECK (estado IN ('programada', 'atendida', 'cancelada')),
    motivo_cancelacion TEXT    NOT NULL DEFAULT '',
    creado_en          TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_citas_fisio_fecha ON citas (fisioterapeuta_id, fecha);
CREATE INDEX IF NOT EXISTS idx_citas_paciente ON citas (paciente_id);

CREATE TABLE IF NOT EXISTS terapias (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    paciente_id       INTEGER NOT NULL REFERENCES pacientes (id),
    fisioterapeuta_id INTEGER NOT NULL REFERENCES usuarios (id),
    cita_id           INTEGER UNIQUE REFERENCES citas (id),
    fecha             TEXT    NOT NULL,
    tipo              TEXT    NOT NULL,
    zona_tratada      TEXT    NOT NULL,
    dolor_inicial     INTEGER NOT NULL CHECK (dolor_inicial BETWEEN 0 AND 10),
    dolor_final       INTEGER NOT NULL CHECK (dolor_final BETWEEN 0 AND 10),
    procedimiento     TEXT    NOT NULL,
    observaciones     TEXT    NOT NULL DEFAULT '',
    creado_en         TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_terapias_paciente ON terapias (paciente_id);
