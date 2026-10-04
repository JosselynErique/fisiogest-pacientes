from __future__ import annotations

from datetime import date
from typing import Protocol

from fisiogest.citas.domain.cita import Cita, CitaDetalle


class CitaRepository(Protocol):
    def guardar(self, cita: Cita) -> Cita: ...

    def obtener(self, cita_id: int) -> Cita | None: ...

    def obtener_detalle(self, cita_id: int) -> CitaDetalle | None: ...

    def activas_del_fisioterapeuta(self, fisioterapeuta_id: int, fecha: date) -> list[Cita]: ...

    def activas_del_paciente(self, paciente_id: int, fecha: date) -> list[Cita]: ...

    def agenda(
        self,
        desde: date,
        hasta: date,
        fisioterapeuta_id: int | None = None,
        paciente_id: int | None = None,
    ) -> list[CitaDetalle]: ...
