from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from fisiogest.shared.domain.errors import Errores

MAX_DIAS_RANGO = 366


@dataclass(frozen=True)
class Periodo:
    desde: date
    hasta: date

    @classmethod
    def crear(cls, desde: date | None, hasta: date | None) -> Periodo:
        errores = Errores()
        if desde is None:
            errores.agregar("desde", "Ingrese la fecha inicial.")
        if hasta is None:
            errores.agregar("hasta", "Ingrese la fecha final.")
        errores.lanzar_si_hay()
        if desde > hasta:
            errores.agregar("hasta", "La fecha final debe ser posterior a la inicial.")
        elif (hasta - desde).days > MAX_DIAS_RANGO:
            errores.agregar("hasta", "El rango máximo del reporte es de un año.")
        errores.lanzar_si_hay()
        return cls(desde, hasta)


@dataclass(frozen=True)
class FilaFisioterapeuta:
    nombre: str
    citas_atendidas: int
    sesiones: int
    pacientes: int
    mejora_promedio: float | None


@dataclass(frozen=True)
class Reporte:
    """RF-08: indicadores de pacientes atendidos, citas y terapias de un periodo."""

    periodo: Periodo
    pacientes_nuevos: int
    pacientes_atendidos: int
    citas_por_estado: dict[str, int]
    sesiones: int
    mejora_promedio: float | None
    terapias_por_tipo: list[tuple[str, int]] = field(default_factory=list)
    por_fisioterapeuta: list[FilaFisioterapeuta] = field(default_factory=list)

    @property
    def total_citas(self) -> int:
        return sum(self.citas_por_estado.values())

    @property
    def tasa_cancelacion(self) -> float:
        total = self.total_citas
        return round(100 * self.citas_por_estado.get("cancelada", 0) / total, 1) if total else 0.0
