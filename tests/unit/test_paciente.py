"""Pruebas unitarias de la entidad Paciente (CP-01, CP-02, CP-03 del plan de pruebas)."""

from datetime import date

import pytest

from fisiogest.pacientes.domain.paciente import DatosPaciente, Paciente
from fisiogest.shared.domain.errors import DomainError, ValidationError
from helpers import CEDULA_1

pytestmark = pytest.mark.unit
HOY = date(2026, 10, 5)


def datos(**cambios) -> DatosPaciente:
    base = {
        "cedula": CEDULA_1,
        "nombres": "sofía",
        "apellidos": "robayo  pérez",
        "fecha_nacimiento": "1995-03-10",
        "telefono": "0999999999",
        "correo": "Sofia@Gmail.com",
        "direccion": "Loja",
    }
    base.update(cambios)
    return DatosPaciente(**base)


def test_cp01_cedula_valida_es_aceptada_y_datos_se_normalizan():
    paciente = Paciente.crear(datos(), hoy=HOY)
    assert paciente.cedula == CEDULA_1
    assert paciente.nombre_completo == "Sofía Robayo Pérez"
    assert paciente.correo == "sofia@gmail.com"
    assert paciente.activo


@pytest.mark.parametrize("campo", ["cedula", "nombres", "apellidos"])
def test_cp02_campos_obligatorios_vacios_impiden_el_registro(campo):
    with pytest.raises(ValidationError) as error:
        Paciente.crear(datos(**{campo: ""}), hoy=HOY)
    assert campo in error.value.errores


def test_cp03_informa_todos_los_errores_a_la_vez():
    with pytest.raises(ValidationError) as error:
        Paciente.crear(
            datos(cedula="123", telefono="12", correo="malo", fecha_nacimiento="2030-01-01"),
            hoy=HOY,
        )
    assert set(error.value.errores) == {"cedula", "telefono", "correo", "fecha_nacimiento"}


def test_campos_opcionales_pueden_quedar_vacios():
    paciente = Paciente.crear(
        DatosPaciente(cedula=CEDULA_1, nombres="Ana", apellidos="Mora"), hoy=HOY
    )
    assert paciente.telefono == "" and paciente.fecha_nacimiento is None


def test_edad_se_calcula_segun_fecha_de_nacimiento():
    paciente = Paciente.crear(datos(fecha_nacimiento="2000-10-06"), hoy=HOY)
    assert paciente.edad(HOY) == 25


def test_actualizar_modifica_datos():
    paciente = Paciente.crear(datos(), hoy=HOY)
    paciente.actualizar(datos(telefono="0981111111", direccion="Puyo"), hoy=HOY)
    assert paciente.telefono == "0981111111"
    assert paciente.direccion == "Puyo"
    assert paciente.actualizado_en is not None


def test_no_se_puede_actualizar_un_paciente_dado_de_baja():
    paciente = Paciente.crear(datos(), hoy=HOY)
    paciente.dar_de_baja()
    with pytest.raises(DomainError):
        paciente.actualizar(datos(), hoy=HOY)


def test_baja_y_reactivacion():
    paciente = Paciente.crear(datos(), hoy=HOY)
    paciente.dar_de_baja()
    assert not paciente.activo
    with pytest.raises(DomainError):
        paciente.dar_de_baja()
    paciente.reactivar()
    assert paciente.activo
