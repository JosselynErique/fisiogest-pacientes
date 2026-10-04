"""RF-02: modificar la información de los pacientes."""

from __future__ import annotations

from fisiogest.pacientes.domain.paciente import DatosPaciente, Paciente
from fisiogest.pacientes.domain.ports import PacienteRepository
from fisiogest.shared.domain.errors import ConflictError, NotFoundError


class ActualizarPaciente:
    def __init__(self, pacientes: PacienteRepository) -> None:
        self._pacientes = pacientes

    def obtener(self, paciente_id: int) -> Paciente:
        paciente = self._pacientes.obtener(paciente_id)
        if paciente is None:
            raise NotFoundError("El paciente no existe.")
        return paciente

    def ejecutar(self, paciente_id: int, datos: DatosPaciente) -> Paciente:
        paciente = self.obtener(paciente_id)
        paciente.actualizar(datos)
        otro = self._pacientes.obtener_por_cedula(paciente.cedula)
        if otro is not None and otro.id != paciente.id:
            raise ConflictError(f"La cédula {paciente.cedula} pertenece a otro paciente.")
        return self._pacientes.guardar(paciente)
