from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from fisiogest.citas.domain.cita import CitaDetalle, EstadoCita
from fisiogest.pacientes.domain.paciente import Paciente
from fisiogest.terapias.domain.terapia import TerapiaDetalle


@dataclass(frozen=True)
class HistorialClinico:
    """Vista consolidada del paciente: datos, citas y sesiones de terapia (RF-07)."""

    paciente: Paciente
    citas: list[CitaDetalle]
    terapias: list[TerapiaDetalle]
    generado_en: datetime

    @property
    def proximas_citas(self) -> list[CitaDetalle]:
        return [
            d
            for d in self.citas
            if d.cita.estado is EstadoCita.PROGRAMADA
            and datetime.combine(d.cita.fecha, d.cita.hora_inicio) >= self.generado_en
        ]

    @property
    def total_sesiones(self) -> int:
        return len(self.terapias)

    @property
    def evolucion_dolor(self) -> tuple[int, int] | None:
        """Dolor de la primera sesión frente al dolor final de la última (EVA)."""
        if not self.terapias:
            return None
        primera, ultima = self.terapias[-1].terapia, self.terapias[0].terapia
        return primera.dolor_inicial, ultima.dolor_final

    @property
    def inasistencias_o_cancelaciones(self) -> int:
        return sum(1 for d in self.citas if d.cita.estado is EstadoCita.CANCELADA)
