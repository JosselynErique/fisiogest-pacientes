"""Adaptador de salida: implementa TerapiaRepository sobre SQLite (patrón DAO)."""

from __future__ import annotations

import sqlite3
from datetime import date, datetime

from fisiogest.shared.infrastructure.database import Database
from fisiogest.terapias.domain.terapia import Terapia, TerapiaDetalle


def _a_terapia(fila: sqlite3.Row) -> Terapia:
    return Terapia(
        id=fila["id"],
        paciente_id=fila["paciente_id"],
        fisioterapeuta_id=fila["fisioterapeuta_id"],
        cita_id=fila["cita_id"],
        fecha=date.fromisoformat(fila["fecha"]),
        tipo=fila["tipo"],
        zona_tratada=fila["zona_tratada"],
        dolor_inicial=fila["dolor_inicial"],
        dolor_final=fila["dolor_final"],
        procedimiento=fila["procedimiento"],
        observaciones=fila["observaciones"],
        creado_en=datetime.fromisoformat(fila["creado_en"]),
    )


class SqliteTerapiaRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    def guardar(self, terapia: Terapia) -> Terapia:
        with self._db.conexion() as con:
            cursor = con.execute(
                """INSERT INTO terapias (paciente_id, fisioterapeuta_id, cita_id, fecha, tipo,
                       zona_tratada, dolor_inicial, dolor_final, procedimiento, observaciones, creado_en)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    terapia.paciente_id,
                    terapia.fisioterapeuta_id,
                    terapia.cita_id,
                    terapia.fecha.isoformat(),
                    terapia.tipo,
                    terapia.zona_tratada,
                    terapia.dolor_inicial,
                    terapia.dolor_final,
                    terapia.procedimiento,
                    terapia.observaciones,
                    terapia.creado_en.isoformat(timespec="seconds"),
                ),
            )
            terapia.id = cursor.lastrowid
        return terapia

    def del_paciente(self, paciente_id: int) -> list[TerapiaDetalle]:
        with self._db.conexion() as con:
            filas = con.execute(
                """SELECT t.*, u.nombre_completo AS fisioterapeuta_nombre
                   FROM terapias t JOIN usuarios u ON u.id = t.fisioterapeuta_id
                   WHERE t.paciente_id = ?
                   ORDER BY t.fecha DESC, t.id DESC""",
                (paciente_id,),
            ).fetchall()
        return [TerapiaDetalle(_a_terapia(f), f["fisioterapeuta_nombre"]) for f in filas]
