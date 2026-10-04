from __future__ import annotations

from typing import Protocol

from fisiogest.reportes.domain.reporte import Periodo, Reporte


class ReporteQuery(Protocol):
    """Puerto de consulta: calcula los indicadores directamente en el almacenamiento."""

    def generar(self, periodo: Periodo) -> Reporte: ...
