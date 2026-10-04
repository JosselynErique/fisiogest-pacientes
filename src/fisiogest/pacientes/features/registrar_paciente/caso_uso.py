"""RF-01: registrar nuevos pacientes con sus datos personales."""

from __future__ import annotations

from fisiogest.pacientes.domain.paciente import DatosPaciente, Paciente
from fisiogest.pacientes.domain.ports import PacienteRepository
from fisiogest.shared.domain.errors import ConflictError


class RegistrarPaciente:
    def __init__(self, pacientes: PacienteRepository) -> None:
        self._pacientes = pacientes

    def ejecutar(self, datos: DatosPaciente) -> Paciente:
        paciente = Paciente.crear(datos)
        if self._pacientes.obtener_por_cedula(paciente.cedula):
            raise ConflictError(
                f"Ya existe un paciente registrado con la cédula {paciente.cedula}."
            )
        return self._pacientes.guardar(paciente)
