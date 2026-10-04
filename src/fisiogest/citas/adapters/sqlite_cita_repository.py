"""Adaptador de salida: implementa CitaRepository sobre SQLite (patrón DAO)."""

from __future__ import annotations

import sqlite3
from datetime import date, datetime, time

from fisiogest.citas.domain.cita import Cita, CitaDetalle, EstadoCita
from fisiogest.shared.infrastructure.database import Database

_SELECT_DETALLE = """
    SELECT c.*, p.nombres || ' ' || p.apellidos AS paciente_nombre, p.cedula AS paciente_cedula,
           u.nombre_completo AS fisioterapeuta_nombre
    FROM citas c
    JOIN pacientes p ON p.id = c.paciente_id
    JOIN usuarios u ON u.id = c.fisioterapeuta_id
"""


def _a_cita(fila: sqlite3.Row) -> Cita:
    return Cita(
        id=fila["id"],
        paciente_id=fila["paciente_id"],
        fisioterapeuta_id=fila["fisioterapeuta_id"],
        fecha=date.fromisoformat(fila["fecha"]),
        hora_inicio=time.fromisoformat(fila["hora_inicio"]),
        hora_fin=time.fromisoformat(fila["hora_fin"]),
        motivo=fila["motivo"],
        estado=EstadoCita(fila["estado"]),
        motivo_cancelacion=fila["motivo_cancelacion"],
        creado_en=datetime.fromisoformat(fila["creado_en"]),
    )


def _a_detalle(fila: sqlite3.Row) -> CitaDetalle:
    return CitaDetalle(
        cita=_a_cita(fila),
        paciente_nombre=fila["paciente_nombre"],
        paciente_cedula=fila["paciente_cedula"],
        fisioterapeuta_nombre=fila["fisioterapeuta_nombre"],
    )


class SqliteCitaRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    def guardar(self, cita: Cita) -> Cita:
        valores = (
            cita.paciente_id,
            cita.fisioterapeuta_id,
            cita.fecha.isoformat(),
            cita.hora_inicio.strftime("%H:%M"),
            cita.hora_fin.strftime("%H:%M"),
            cita.motivo,
            cita.estado.value,
            cita.motivo_cancelacion,
        )
        with self._db.conexion() as con:
            if cita.id is None:
                cursor = con.execute(
                    """INSERT INTO citas (paciente_id, fisioterapeuta_id, fecha, hora_inicio, hora_fin,
                           motivo, estado, motivo_cancelacion, creado_en)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (*valores, cita.creado_en.isoformat(timespec="seconds")),
                )
                cita.id = cursor.lastrowid
            else:
                con.execute(
                    """UPDATE citas SET paciente_id = ?, fisioterapeuta_id = ?, fecha = ?,
                           hora_inicio = ?, hora_fin = ?, motivo = ?, estado = ?, motivo_cancelacion = ?
                       WHERE id = ?""",
                    (*valores, cita.id),
                )
        return cita

    def obtener(self, cita_id: int) -> Cita | None:
        with self._db.conexion() as con:
            fila = con.execute("SELECT * FROM citas WHERE id = ?", (cita_id,)).fetchone()
        return _a_cita(fila) if fila else None

    def obtener_detalle(self, cita_id: int) -> CitaDetalle | None:
        with self._db.conexion() as con:
            fila = con.execute(_SELECT_DETALLE + " WHERE c.id = ?", (cita_id,)).fetchone()
        return _a_detalle(fila) if fila else None

    def _activas(self, columna: str, valor: int, fecha: date) -> list[Cita]:
        with self._db.conexion() as con:
            filas = con.execute(
                f"SELECT * FROM citas WHERE {columna} = ? AND fecha = ? AND estado != 'cancelada'",
                (valor, fecha.isoformat()),
            ).fetchall()
        return [_a_cita(f) for f in filas]

    def activas_del_fisioterapeuta(self, fisioterapeuta_id: int, fecha: date) -> list[Cita]:
        return self._activas("fisioterapeuta_id", fisioterapeuta_id, fecha)

    def activas_del_paciente(self, paciente_id: int, fecha: date) -> list[Cita]:
        return self._activas("paciente_id", paciente_id, fecha)

    def agenda(
        self,
        desde: date,
        hasta: date,
        fisioterapeuta_id: int | None = None,
        paciente_id: int | None = None,
    ) -> list[CitaDetalle]:
        sql = _SELECT_DETALLE + " WHERE c.fecha BETWEEN ? AND ?"
        params: list[object] = [desde.isoformat(), hasta.isoformat()]
        if fisioterapeuta_id is not None:
            sql += " AND c.fisioterapeuta_id = ?"
            params.append(fisioterapeuta_id)
        if paciente_id is not None:
            sql += " AND c.paciente_id = ?"
            params.append(paciente_id)
        sql += " ORDER BY c.fecha, c.hora_inicio, u.nombre_completo"
        with self._db.conexion() as con:
            return [_a_detalle(f) for f in con.execute(sql, params).fetchall()]
