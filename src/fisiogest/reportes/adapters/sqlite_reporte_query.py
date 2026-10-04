"""Adaptador de salida: calcula los indicadores del reporte con consultas SQL agregadas."""

from __future__ import annotations

from fisiogest.reportes.domain.reporte import FilaFisioterapeuta, Periodo, Reporte
from fisiogest.shared.infrastructure.database import Database


def _redondear(valor: float | None) -> float | None:
    return round(valor, 1) if valor is not None else None


class SqliteReporteQuery:
    def __init__(self, db: Database) -> None:
        self._db = db

    def generar(self, periodo: Periodo) -> Reporte:
        rango = (periodo.desde.isoformat(), periodo.hasta.isoformat())
        with self._db.conexion() as con:
            pacientes_nuevos = con.execute(
                "SELECT COUNT(*) FROM pacientes WHERE date(creado_en) BETWEEN ? AND ?", rango
            ).fetchone()[0]
            pacientes_atendidos, sesiones, mejora = con.execute(
                """SELECT COUNT(DISTINCT paciente_id), COUNT(*), AVG(dolor_inicial - dolor_final)
                   FROM terapias WHERE fecha BETWEEN ? AND ?""",
                rango,
            ).fetchone()
            citas_por_estado = {"programada": 0, "atendida": 0, "cancelada": 0}
            for estado, total in con.execute(
                "SELECT estado, COUNT(*) FROM citas WHERE fecha BETWEEN ? AND ? GROUP BY estado",
                rango,
            ):
                citas_por_estado[estado] = total
            terapias_por_tipo = [
                (tipo, total)
                for tipo, total in con.execute(
                    """SELECT tipo, COUNT(*) AS total FROM terapias WHERE fecha BETWEEN ? AND ?
                       GROUP BY tipo ORDER BY total DESC, tipo""",
                    rango,
                )
            ]
            por_fisio = [
                FilaFisioterapeuta(
                    nombre=f["nombre_completo"],
                    citas_atendidas=f["citas_atendidas"],
                    sesiones=f["sesiones"],
                    pacientes=f["pacientes"],
                    mejora_promedio=_redondear(f["mejora"]),
                )
                for f in con.execute(
                    """SELECT u.nombre_completo,
                           (SELECT COUNT(*) FROM citas c WHERE c.fisioterapeuta_id = u.id
                              AND c.estado = 'atendida' AND c.fecha BETWEEN :desde AND :hasta) AS citas_atendidas,
                           COUNT(t.id) AS sesiones,
                           COUNT(DISTINCT t.paciente_id) AS pacientes,
                           AVG(t.dolor_inicial - t.dolor_final) AS mejora
                       FROM usuarios u
                       LEFT JOIN terapias t ON t.fisioterapeuta_id = u.id AND t.fecha BETWEEN :desde AND :hasta
                       WHERE u.rol = 'fisioterapeuta'
                       GROUP BY u.id ORDER BY sesiones DESC, u.nombre_completo""",
                    {"desde": rango[0], "hasta": rango[1]},
                )
            ]
        return Reporte(
            periodo=periodo,
            pacientes_nuevos=pacientes_nuevos,
            pacientes_atendidos=pacientes_atendidos,
            citas_por_estado=citas_por_estado,
            sesiones=sesiones,
            mejora_promedio=_redondear(mejora),
            terapias_por_tipo=terapias_por_tipo,
            por_fisioterapeuta=por_fisio,
        )
