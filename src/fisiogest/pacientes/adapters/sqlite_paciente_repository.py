"""Adaptador de salida: implementa PacienteRepository sobre SQLite (patrón DAO)."""

from __future__ import annotations

import sqlite3
from datetime import date, datetime

from fisiogest.pacientes.domain.paciente import Paciente
from fisiogest.shared.infrastructure.database import Database

_CAMPOS = (
    "cedula, nombres, apellidos, fecha_nacimiento, telefono, correo, direccion, "
    "contacto_emergencia, activo"
)


def _a_paciente(fila: sqlite3.Row) -> Paciente:
    return Paciente(
        id=fila["id"],
        cedula=fila["cedula"],
        nombres=fila["nombres"],
        apellidos=fila["apellidos"],
        fecha_nacimiento=(
            date.fromisoformat(fila["fecha_nacimiento"]) if fila["fecha_nacimiento"] else None
        ),
        telefono=fila["telefono"],
        correo=fila["correo"],
        direccion=fila["direccion"],
        contacto_emergencia=fila["contacto_emergencia"],
        activo=bool(fila["activo"]),
        creado_en=datetime.fromisoformat(fila["creado_en"]),
        actualizado_en=(
            datetime.fromisoformat(fila["actualizado_en"]) if fila["actualizado_en"] else None
        ),
    )


class SqlitePacienteRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    def guardar(self, paciente: Paciente) -> Paciente:
        valores = (
            paciente.cedula,
            paciente.nombres,
            paciente.apellidos,
            paciente.fecha_nacimiento.isoformat() if paciente.fecha_nacimiento else None,
            paciente.telefono,
            paciente.correo,
            paciente.direccion,
            paciente.contacto_emergencia,
            int(paciente.activo),
        )
        with self._db.conexion() as con:
            if paciente.id is None:
                cursor = con.execute(
                    f"INSERT INTO pacientes ({_CAMPOS}, creado_en) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (*valores, paciente.creado_en.isoformat(timespec="seconds")),
                )
                paciente.id = cursor.lastrowid
            else:
                con.execute(
                    """UPDATE pacientes SET cedula = ?, nombres = ?, apellidos = ?,
                           fecha_nacimiento = ?, telefono = ?, correo = ?, direccion = ?,
                           contacto_emergencia = ?, activo = ?, actualizado_en = ?
                       WHERE id = ?""",
                    (
                        *valores,
                        (paciente.actualizado_en or datetime.now()).isoformat(timespec="seconds"),
                        paciente.id,
                    ),
                )
        return paciente

    def obtener(self, paciente_id: int) -> Paciente | None:
        with self._db.conexion() as con:
            fila = con.execute("SELECT * FROM pacientes WHERE id = ?", (paciente_id,)).fetchone()
        return _a_paciente(fila) if fila else None

    def obtener_por_cedula(self, cedula: str) -> Paciente | None:
        with self._db.conexion() as con:
            fila = con.execute("SELECT * FROM pacientes WHERE cedula = ?", (cedula,)).fetchone()
        return _a_paciente(fila) if fila else None

    def buscar(self, texto: str = "", incluir_inactivos: bool = False) -> list[Paciente]:
        sql = "SELECT * FROM pacientes WHERE 1 = 1"
        params: list[object] = []
        if not incluir_inactivos:
            sql += " AND activo = 1"
        for palabra in texto.split():
            sql += " AND (cedula LIKE ? OR nombres LIKE ? OR apellidos LIKE ?)"
            patron = f"%{palabra}%"
            params += [patron, patron, patron]
        sql += " ORDER BY apellidos, nombres"
        with self._db.conexion() as con:
            return [_a_paciente(f) for f in con.execute(sql, params).fetchall()]

    def contar(self, solo_activos: bool = True) -> int:
        sql = "SELECT COUNT(*) FROM pacientes" + (" WHERE activo = 1" if solo_activos else "")
        with self._db.conexion() as con:
            return con.execute(sql).fetchone()[0]
