from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime

from fisiogest.shared.domain.errors import Errores
from fisiogest.shared.domain.validators import limpiar, parsear_entero, parsear_fecha

TIPOS_TERAPIA = (
    "Terapia manual",
    "Ejercicio terapéutico",
    "Electroterapia (TENS / EMS)",
    "Ultrasonido terapéutico",
    "Termoterapia / Crioterapia",
    "Masoterapia",
    "Punción seca",
    "Vendaje neuromuscular",
    "Rehabilitación postquirúrgica",
    "Otro",
)


@dataclass(frozen=True)
class DatosTerapia:
    fecha: str = ""
    tipo: str = ""
    zona_tratada: str = ""
    dolor_inicial: str | int = ""
    dolor_final: str | int = ""
    procedimiento: str = ""
    observaciones: str = ""


@dataclass
class Terapia:
    """Sesión de terapia registrada por el fisioterapeuta (RF-06).

    El dolor se mide con la Escala Visual Analógica (EVA) de 0 a 10.
    """

    paciente_id: int
    fisioterapeuta_id: int
    fecha: date
    tipo: str
    zona_tratada: str
    dolor_inicial: int
    dolor_final: int
    procedimiento: str
    observaciones: str = ""
    cita_id: int | None = None
    id: int | None = None
    creado_en: datetime = field(default_factory=lambda: datetime.now().replace(microsecond=0))

    @classmethod
    def registrar(
        cls,
        datos: DatosTerapia,
        paciente_id: int,
        fisioterapeuta_id: int,
        hoy: date,
        cita_id: int | None = None,
    ) -> Terapia:
        errores = Errores()
        fecha = parsear_fecha(str(datos.fecha))
        dolor_inicial = parsear_entero(datos.dolor_inicial)
        dolor_final = parsear_entero(datos.dolor_final)
        zona = limpiar(datos.zona_tratada)
        procedimiento = limpiar(datos.procedimiento)

        if fecha is None:
            errores.agregar("fecha", "Ingrese la fecha de la sesión.")
        elif fecha > hoy:
            errores.agregar("fecha", "No se puede registrar una sesión con fecha futura.")
        if datos.tipo not in TIPOS_TERAPIA:
            errores.agregar("tipo", "Seleccione el tipo de terapia.")
        if len(zona) < 3:
            errores.agregar("zona_tratada", "Indique la zona tratada.")
        if dolor_inicial is None or not 0 <= dolor_inicial <= 10:
            errores.agregar("dolor_inicial", "El dolor inicial debe estar entre 0 y 10 (EVA).")
        if dolor_final is None or not 0 <= dolor_final <= 10:
            errores.agregar("dolor_final", "El dolor final debe estar entre 0 y 10 (EVA).")
        if len(procedimiento) < 5:
            errores.agregar("procedimiento", "Describa el procedimiento realizado.")
        errores.lanzar_si_hay()

        return cls(
            paciente_id=paciente_id,
            fisioterapeuta_id=fisioterapeuta_id,
            fecha=fecha,
            tipo=datos.tipo,
            zona_tratada=zona,
            dolor_inicial=dolor_inicial,
            dolor_final=dolor_final,
            procedimiento=procedimiento,
            observaciones=limpiar(datos.observaciones),
            cita_id=cita_id,
        )

    @property
    def mejora_dolor(self) -> int:
        """Puntos de dolor reducidos durante la sesión (positivo = mejoró)."""
        return self.dolor_inicial - self.dolor_final


@dataclass(frozen=True)
class TerapiaDetalle:
    terapia: Terapia
    fisioterapeuta_nombre: str
