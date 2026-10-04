"""Panel de inicio: resumen del día adaptado al rol del usuario."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from fisiogest.citas.domain.cita import CitaDetalle, EstadoCita
from fisiogest.citas.domain.ports import CitaRepository
from fisiogest.pacientes.domain.ports import PacienteRepository
from fisiogest.reportes.domain.ports import ReporteQuery
from fisiogest.reportes.domain.reporte import Periodo
from fisiogest.usuarios.domain.usuario import Rol, Usuario


@dataclass(frozen=True)
class ResumenPanel:
    pacientes_activos: int
    citas_hoy: list[CitaDetalle]
    sesiones_mes: int
    pacientes_atendidos_mes: int

    @property
    def pendientes_hoy(self) -> list[CitaDetalle]:
        return [d for d in self.citas_hoy if d.cita.estado is EstadoCita.PROGRAMADA]


class VerPanel:
    def __init__(
        self,
        pacientes: PacienteRepository,
        citas: CitaRepository,
        reportes: ReporteQuery,
        reloj: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._pacientes = pacientes
        self._citas = citas
        self._reportes = reportes
        self._reloj = reloj

    def ejecutar(self, usuario: Usuario) -> ResumenPanel:
        hoy = self._reloj().date()
        fisio_id = usuario.id if usuario.rol is Rol.FISIOTERAPEUTA else None
        mes = self._reportes.generar(Periodo(hoy.replace(day=1), hoy))
        return ResumenPanel(
            pacientes_activos=self._pacientes.contar(),
            citas_hoy=self._citas.agenda(hoy, hoy, fisioterapeuta_id=fisio_id),
            sesiones_mes=mes.sesiones,
            pacientes_atendidos_mes=mes.pacientes_atendidos,
        )
