from __future__ import annotations

from typing import Protocol

from fisiogest.pacientes.domain.paciente import Paciente


class PacienteRepository(Protocol):
    def guardar(self, paciente: Paciente) -> Paciente: ...

    def obtener(self, paciente_id: int) -> Paciente | None: ...

    def obtener_por_cedula(self, cedula: str) -> Paciente | None: ...

    def buscar(self, texto: str = "", incluir_inactivos: bool = False) -> list[Paciente]: ...

    def contar(self, solo_activos: bool = True) -> int: ...
