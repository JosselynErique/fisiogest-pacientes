"""RF-04 y RF-05: agendar citas sin cruces de horario."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from fisiogest.citas.domain.cita import Cita, DatosCita
from fisiogest.citas.domain.ports import CitaRepository
from fisiogest.pacientes.domain.ports import PacienteRepository
from fisiogest.shared.domain.errors import ConflictError, Errores
from fisiogest.usuarios.domain.ports import UsuarioRepository
from fisiogest.usuarios.domain.usuario import Rol


class AgendarCita:
    def __init__(
        self,
        citas: CitaRepository,
        pacientes: PacienteRepository,
        usuarios: UsuarioRepository,
        reloj: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._citas = citas
        self._pacientes = pacientes
        self._usuarios = usuarios
        self._reloj = reloj

    def ejecutar(self, datos: DatosCita) -> Cita:
        cita = Cita.programar(datos, self._reloj())

        errores = Errores()
        paciente = self._pacientes.obtener(cita.paciente_id)
        if paciente is None or not paciente.activo:
            errores.agregar("paciente_id", "El paciente no existe o está dado de baja.")
        fisio = self._usuarios.obtener(cita.fisioterapeuta_id)
        if fisio is None or not fisio.activo or fisio.rol is not Rol.FISIOTERAPEUTA:
            errores.agregar("fisioterapeuta_id", "Seleccione un fisioterapeuta activo.")
        errores.lanzar_si_hay()

        for existente in self._citas.activas_del_fisioterapeuta(cita.fisioterapeuta_id, cita.fecha):
            if cita.se_solapa_con(existente):
                raise ConflictError(
                    f"{fisio.nombre_completo} ya tiene una cita de "
                    f"{existente.hora_inicio:%H:%M} a {existente.hora_fin:%H:%M} ese día."
                )
        for existente in self._citas.activas_del_paciente(cita.paciente_id, cita.fecha):
            if cita.se_solapa_con(existente):
                raise ConflictError(
                    f"El paciente ya tiene otra cita de "
                    f"{existente.hora_inicio:%H:%M} a {existente.hora_fin:%H:%M} ese día."
                )
        return self._citas.guardar(cita)
