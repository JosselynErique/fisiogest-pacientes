"""Consulta de la agenda diaria. Un fisioterapeuta solo ve sus propias citas."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from fisiogest.citas.domain.cita import CitaDetalle, EstadoCita
from fisiogest.citas.domain.ports import CitaRepository
from fisiogest.usuarios.domain.usuario import Rol, Usuario


@dataclass(frozen=True)
class Agenda:
    fecha: date
    citas: list[CitaDetalle]

    @property
    def programadas(self) -> int:
        return sum(1 for d in self.citas if d.cita.estado is EstadoCita.PROGRAMADA)

    @property
    def atendidas(self) -> int:
        return sum(1 for d in self.citas if d.cita.estado is EstadoCita.ATENDIDA)

    @property
    def canceladas(self) -> int:
        return sum(1 for d in self.citas if d.cita.estado is EstadoCita.CANCELADA)


class ConsultarAgenda:
    def __init__(self, citas: CitaRepository) -> None:
        self._citas = citas

    def ejecutar(
        self, fecha: date, solicitante: Usuario, fisioterapeuta_id: int | None = None
    ) -> Agenda:
        if solicitante.rol is Rol.FISIOTERAPEUTA:
            fisioterapeuta_id = solicitante.id
        return Agenda(fecha, self._citas.agenda(fecha, fecha, fisioterapeuta_id=fisioterapeuta_id))
