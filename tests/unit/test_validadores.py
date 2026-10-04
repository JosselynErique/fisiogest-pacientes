import pytest

from fisiogest.shared.domain.validators import (
    es_cedula_valida,
    es_correo_valido,
    es_telefono_valido,
    limpiar,
)

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("cedula", ["1722601810", "0909139099", "2238657973", "0524323193"])
def test_cedulas_validas(cedula):
    assert es_cedula_valida(cedula)


@pytest.mark.parametrize(
    "cedula, motivo",
    [
        ("1722601811", "dígito verificador incorrecto"),
        ("1104567890", "dígito verificador incorrecto"),
        ("172260181", "menos de 10 dígitos"),
        ("17226018100", "más de 10 dígitos"),
        ("17A2601810", "contiene letras"),
        ("2522601810", "provincia inexistente"),
        ("1772601810", "tercer dígito mayor a 5"),
        ("", "vacía"),
    ],
)
def test_cedulas_invalidas(cedula, motivo):
    assert not es_cedula_valida(cedula), motivo


@pytest.mark.parametrize("correo", ["ana@correo.ec", "luis.taco@uea.edu.ec"])
def test_correos_validos(correo):
    assert es_correo_valido(correo)


@pytest.mark.parametrize("correo", ["ana", "ana@", "ana@correo", "ana correo@x.com"])
def test_correos_invalidos(correo):
    assert not es_correo_valido(correo)


@pytest.mark.parametrize(
    "telefono, valido",
    [("0991234567", True), ("032885123", True), ("991234567", False), ("09912", False)],
)
def test_telefonos(telefono, valido):
    assert es_telefono_valido(telefono) is valido


def test_limpiar_quita_espacios_sobrantes():
    assert limpiar("  Ana   Lucía  ") == "Ana Lucía"
    assert limpiar(None) == ""
