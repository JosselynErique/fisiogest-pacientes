"""RF-06: el fisioterapeuta registra las terapias realizadas y sus observaciones."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from fisiogest.citas.domain.cita import Cita, EstadoCita
from fisiogest.citas.domain.ports import CitaRepository
from fisiogest.pacientes.domain.paciente import Paciente
from fisiogest.pacientes.domain.ports import PacienteRepository
from fisiogest.shared.domain.errors import DomainError, NotFoundError
from fisiogest.terapias.domain.ports import TerapiaRepository
from fisiogest.terapias.domain.terapia import DatosTerapia, Terapia
from fisiogest.usuarios.domain.usuario import Rol, Usuario


class RegistrarTerapia:
    def __init__(
        self,
        terapias: TerapiaRepository,
        pacientes: PacienteRepository,
        citas: CitaRepository,
        reloj: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._terapias = terapias
        self._pacientes = pacientes
        self._citas = citas
        self._reloj = reloj

    def paciente(self, paciente_id: int) -> Paciente:
        paciente = self._pacientes.obtener(paciente_id)
        if paciente is None:
            raise NotFoundError("El paciente no existe.")
        return paciente

    def cita_para_atender(self, cita_id: int, solicitante: Usuario) -> Cita:
        cita = self._citas.obtener(cita_id)
        if cita is None:
            raise NotFoundError("La cita no existe.")
        if cita.estado is not EstadoCita.PROGRAMADA:
            raise DomainError("La cita ya fue atendida o cancelada.")
        if solicitante.rol is not Rol.ADMINISTRADOR and solicitante.id != cita.fisioterapeuta_id:
            raise DomainError("Solo el fisioterapeuta asignado puede atender esta cita.")
        return cita

    def desde_cita(self, cita_id: int, datos: DatosTerapia, solicitante: Usuario) -> Terapia:
        """Registra la sesión de una cita agendada y la marca como ATENDIDA."""
        cita = self.cita_para_atender(cita_id, solicitante)
        terapia = Terapia.registrar(
            datos,
            paciente_id=cita.paciente_id,
            fisioterapeuta_id=cita.fisioterapeuta_id,
            hoy=self._reloj().date(),
            cita_id=cita.id,
        )
        cita.marcar_atendida()
        terapia = self._terapias.guardar(terapia)
        self._citas.guardar(cita)
        return terapia

    def sin_cita(self, paciente_id: int, datos: DatosTerapia, solicitante: Usuario) -> Terapia:
        """Registra una sesión no agendada (p. ej. atención inmediata)."""
        if solicitante.rol is not Rol.FISIOTERAPEUTA:
            raise DomainError("Solo un fisioterapeuta puede registrar sesiones sin cita.")
        paciente = self.paciente(paciente_id)
        if not paciente.activo:
            raise DomainError("El paciente está dado de baja.")
        terapia = Terapia.registrar(
            datos,
            paciente_id=paciente.id,
            fisioterapeuta_id=solicitante.id,
            hoy=self._reloj().date(),
        )
        return self._terapias.guardar(terapia)
