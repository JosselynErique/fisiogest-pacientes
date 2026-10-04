"""RF-07: consultar el historial clínico completo de cada paciente."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime

from fisiogest.citas.domain.ports import CitaRepository
from fisiogest.historial.domain.historial import HistorialClinico
from fisiogest.pacientes.domain.ports import PacienteRepository
from fisiogest.shared.domain.errors import NotFoundError
from fisiogest.terapias.domain.ports import TerapiaRepository


class ConsultarHistorial:
    def __init__(
        self,
        pacientes: PacienteRepository,
        citas: CitaRepository,
        terapias: TerapiaRepository,
        reloj: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._pacientes = pacientes
        self._citas = citas
        self._terapias = terapias
        self._reloj = reloj

    def ejecutar(self, paciente_id: int) -> HistorialClinico:
        paciente = self._pacientes.obtener(paciente_id)
        if paciente is None:
            raise NotFoundError("El paciente no existe.")
        citas = self._citas.agenda(date.min, date.max, paciente_id=paciente_id)
        citas.sort(key=lambda d: (d.cita.fecha, d.cita.hora_inicio), reverse=True)
        return HistorialClinico(
            paciente=paciente,
            citas=citas,
            terapias=self._terapias.del_paciente(paciente_id),
            generado_en=self._reloj(),
        )
