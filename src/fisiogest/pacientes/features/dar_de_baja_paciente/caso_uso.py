"""RF-03: eliminar (dar de baja) registros de pacientes.

Se aplica una baja lógica: el historial clínico debe conservarse, por lo que el
registro se marca como inactivo y deja de aparecer en búsquedas y agendamiento.
"""

from __future__ import annotations

from fisiogest.pacientes.domain.paciente import Paciente
from fisiogest.pacientes.domain.ports import PacienteRepository
from fisiogest.shared.domain.errors import NotFoundError


class DarDeBajaPaciente:
    def __init__(self, pacientes: PacienteRepository) -> None:
        self._pacientes = pacientes

    def _obtener(self, paciente_id: int) -> Paciente:
        paciente = self._pacientes.obtener(paciente_id)
        if paciente is None:
            raise NotFoundError("El paciente no existe.")
        return paciente

    def ejecutar(self, paciente_id: int) -> Paciente:
        paciente = self._obtener(paciente_id)
        paciente.dar_de_baja()
        return self._pacientes.guardar(paciente)

    def reactivar(self, paciente_id: int) -> Paciente:
        paciente = self._obtener(paciente_id)
        paciente.reactivar()
        return self._pacientes.guardar(paciente)
