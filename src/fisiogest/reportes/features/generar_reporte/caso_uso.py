"""RF-08: el administrador genera reportes de pacientes atendidos, citas y terapias."""

from __future__ import annotations

from datetime import date

from fisiogest.reportes.domain.ports import ReporteQuery
from fisiogest.reportes.domain.reporte import Periodo, Reporte


class GenerarReporte:
    def __init__(self, consulta: ReporteQuery) -> None:
        self._consulta = consulta

    def ejecutar(self, desde: date | None, hasta: date | None) -> Reporte:
        return self._consulta.generar(Periodo.crear(desde, hasta))
