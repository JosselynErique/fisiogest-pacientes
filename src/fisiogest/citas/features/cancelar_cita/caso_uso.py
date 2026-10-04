"""RF-10: cancelar una cita previamente agendada, actualizando su estado en la agenda."""

from __future__ import annotations

from fisiogest.citas.domain.cita import Cita, CitaDetalle
from fisiogest.citas.domain.ports import CitaRepository
from fisiogest.shared.domain.errors import NotFoundError


class CancelarCita:
    def __init__(self, citas: CitaRepository) -> None:
        self._citas = citas

    def detalle(self, cita_id: int) -> CitaDetalle:
        detalle = self._citas.obtener_detalle(cita_id)
        if detalle is None:
            raise NotFoundError("La cita no existe.")
        return detalle

    def ejecutar(self, cita_id: int, motivo: str) -> Cita:
        cita = self._citas.obtener(cita_id)
        if cita is None:
            raise NotFoundError("La cita no existe.")
        cita.cancelar(motivo)
        return self._citas.guardar(cita)
