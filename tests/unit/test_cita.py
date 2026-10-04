"""Reglas de negocio de las citas (RF-04, RF-05, RF-10)."""

from datetime import datetime, time

import pytest

from fisiogest.citas.domain.cita import Cita, DatosCita, EstadoCita
from fisiogest.shared.domain.errors import DomainError, ValidationError

pytestmark = pytest.mark.unit
AHORA = datetime(2026, 10, 5, 8, 0)  # lunes


def nueva(**cambios) -> Cita:
    base = {
        "paciente_id": 1,
        "fisioterapeuta_id": 2,
        "fecha": "2026-10-06",
        "hora_inicio": "10:00",
        "duracion_minutos": "45",
    }
    base.update(cambios)
    return Cita.programar(DatosCita(**base), AHORA)


def test_programar_calcula_hora_fin_y_queda_programada():
    cita = nueva()
    assert cita.hora_fin == time(10, 45)
    assert cita.estado is EstadoCita.PROGRAMADA


@pytest.mark.parametrize(
    "cambios, campo",
    [
        ({"fecha": "2026-10-04"}, "fecha"),  # pasado
        ({"fecha": "2026-10-11"}, "fecha"),  # domingo
        ({"hora_inicio": "06:30"}, "hora_inicio"),  # antes de apertura
        ({"hora_inicio": "19:30"}, "hora_inicio"),  # termina después del cierre
        ({"duracion_minutos": "20"}, "duracion_minutos"),
        ({"paciente_id": ""}, "paciente_id"),
        ({"fisioterapeuta_id": "x"}, "fisioterapeuta_id"),
        ({"hora_inicio": "25:00"}, "hora_inicio"),
    ],
)
def test_validaciones_al_programar(cambios, campo):
    with pytest.raises(ValidationError) as error:
        nueva(**cambios)
    assert campo in error.value.errores


@pytest.mark.parametrize(
    "inicio, duracion, se_solapan",
    [
        ("10:00", 45, True),  # mismo horario
        ("10:30", 45, True),  # empieza durante la otra
        ("09:30", 45, True),  # termina durante la otra
        ("10:45", 45, False),  # empieza justo al terminar
        ("09:15", 45, False),  # termina justo al empezar
        ("14:00", 60, False),
    ],
)
def test_rf05_deteccion_de_solapamiento(inicio, duracion, se_solapan):
    existente = nueva()
    existente.id = 1
    otra = nueva(hora_inicio=inicio, duracion_minutos=str(duracion))
    assert otra.se_solapa_con(existente) is se_solapan


def test_una_cita_cancelada_no_bloquea_el_horario():
    existente = nueva()
    existente.id = 1
    existente.cancelar("Paciente enfermo")
    assert not nueva().se_solapa_con(existente)


def test_rf10_cancelar_exige_motivo_y_cambia_estado():
    cita = nueva()
    with pytest.raises(ValidationError):
        cita.cancelar("  ")
    cita.cancelar("El paciente reprogramará")
    assert cita.estado is EstadoCita.CANCELADA
    assert cita.motivo_cancelacion == "El paciente reprogramará"


def test_no_se_cancela_una_cita_atendida():
    cita = nueva()
    cita.marcar_atendida()
    with pytest.raises(DomainError):
        cita.cancelar("Motivo cualquiera")
    with pytest.raises(DomainError):
        cita.marcar_atendida()
