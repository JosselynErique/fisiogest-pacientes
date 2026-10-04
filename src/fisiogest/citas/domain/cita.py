from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from enum import Enum

from fisiogest.shared.domain.errors import DomainError, Errores
from fisiogest.shared.domain.validators import limpiar, parsear_entero, parsear_fecha, parsear_hora

HORA_APERTURA = time(7, 0)
HORA_CIERRE = time(20, 0)
DURACIONES_MINUTOS = (30, 45, 60, 90)


class EstadoCita(str, Enum):
    PROGRAMADA = "programada"
    ATENDIDA = "atendida"
    CANCELADA = "cancelada"

    @property
    def etiqueta(self) -> str:
        return self.value.capitalize()


@dataclass(frozen=True)
class DatosCita:
    paciente_id: str | int = ""
    fisioterapeuta_id: str | int = ""
    fecha: str = ""
    hora_inicio: str = ""
    duracion_minutos: str | int = "45"
    motivo: str = ""


@dataclass
class Cita:
    paciente_id: int
    fisioterapeuta_id: int
    fecha: date
    hora_inicio: time
    hora_fin: time
    motivo: str = ""
    estado: EstadoCita = EstadoCita.PROGRAMADA
    motivo_cancelacion: str = ""
    id: int | None = None
    creado_en: datetime = field(default_factory=datetime.now)

    @classmethod
    def programar(cls, datos: DatosCita, ahora: datetime) -> Cita:
        """RF-04: valida los datos de una nueva cita y la crea en estado PROGRAMADA."""
        errores = Errores()
        paciente_id = parsear_entero(datos.paciente_id)
        fisioterapeuta_id = parsear_entero(datos.fisioterapeuta_id)
        fecha = parsear_fecha(str(datos.fecha))
        inicio = parsear_hora(str(datos.hora_inicio))
        duracion = parsear_entero(datos.duracion_minutos)

        if not paciente_id:
            errores.agregar("paciente_id", "Seleccione el paciente.")
        if not fisioterapeuta_id:
            errores.agregar("fisioterapeuta_id", "Seleccione el fisioterapeuta responsable.")
        if fecha is None:
            errores.agregar("fecha", "Ingrese una fecha válida.")
        elif fecha.weekday() == 6:
            errores.agregar("fecha", "El consultorio no atiende los domingos.")
        if inicio is None:
            errores.agregar("hora_inicio", "Ingrese una hora válida (HH:MM).")
        if duracion not in DURACIONES_MINUTOS:
            errores.agregar("duracion_minutos", "Seleccione una duración válida.")
        errores.lanzar_si_hay()

        inicio_dt = datetime.combine(fecha, inicio)
        fin_dt = inicio_dt + timedelta(minutes=duracion)
        if inicio < HORA_APERTURA or fin_dt.time() > HORA_CIERRE or fin_dt.date() != fecha:
            errores.agregar(
                "hora_inicio", "La cita debe estar dentro del horario de atención (07:00 a 20:00)."
            )
        if inicio_dt < ahora:
            errores.agregar("fecha", "No se pueden agendar citas en fechas u horas pasadas.")
        errores.lanzar_si_hay()

        return cls(
            paciente_id=paciente_id,
            fisioterapeuta_id=fisioterapeuta_id,
            fecha=fecha,
            hora_inicio=inicio,
            hora_fin=fin_dt.time(),
            motivo=limpiar(datos.motivo),
        )

    @property
    def esta_activa(self) -> bool:
        return self.estado is not EstadoCita.CANCELADA

    def se_solapa_con(self, otra: Cita) -> bool:
        """RF-05: dos citas activas del mismo día se solapan si sus intervalos se cruzan."""
        if self.id is not None and self.id == otra.id:
            return False
        if not (self.esta_activa and otra.esta_activa) or self.fecha != otra.fecha:
            return False
        return self.hora_inicio < otra.hora_fin and otra.hora_inicio < self.hora_fin

    def cancelar(self, motivo: str) -> None:
        """RF-10: cancela la cita y actualiza su estado en la agenda."""
        if self.estado is not EstadoCita.PROGRAMADA:
            raise DomainError(
                f"Solo se pueden cancelar citas programadas (estado actual: {self.estado.etiqueta})."
            )
        motivo = limpiar(motivo)
        if len(motivo) < 3:
            errores = Errores()
            errores.agregar("motivo_cancelacion", "Indique el motivo de la cancelación.")
            errores.lanzar_si_hay()
        self.estado = EstadoCita.CANCELADA
        self.motivo_cancelacion = motivo

    def marcar_atendida(self) -> None:
        if self.estado is not EstadoCita.PROGRAMADA:
            raise DomainError("La cita ya no está programada; no se puede registrar su atención.")
        self.estado = EstadoCita.ATENDIDA


@dataclass(frozen=True)
class CitaDetalle:
    """Modelo de lectura para la agenda: la cita con los nombres ya resueltos."""

    cita: Cita
    paciente_nombre: str
    paciente_cedula: str
    fisioterapeuta_nombre: str
