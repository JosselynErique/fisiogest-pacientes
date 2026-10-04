from __future__ import annotations

from typing import Protocol

from fisiogest.terapias.domain.terapia import Terapia, TerapiaDetalle


class TerapiaRepository(Protocol):
    def guardar(self, terapia: Terapia) -> Terapia: ...

    def del_paciente(self, paciente_id: int) -> list[TerapiaDetalle]: ...
