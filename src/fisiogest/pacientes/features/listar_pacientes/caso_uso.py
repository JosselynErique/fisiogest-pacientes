"""Consulta y búsqueda de pacientes por cédula, nombres o apellidos."""

from __future__ import annotations

from fisiogest.pacientes.domain.paciente import Paciente
from fisiogest.pacientes.domain.ports import PacienteRepository


class ListarPacientes:
    def __init__(self, pacientes: PacienteRepository) -> None:
        self._pacientes = pacientes

    def ejecutar(self, texto: str = "", incluir_inactivos: bool = False) -> list[Paciente]:
        return self._pacientes.buscar(texto.strip(), incluir_inactivos)
