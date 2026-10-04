"""Reglas de las entidades Usuario, Terapia y Periodo de reporte."""

from datetime import date, datetime, timedelta

import pytest

from fisiogest.reportes.domain.reporte import Periodo
from fisiogest.shared.domain.errors import ValidationError
from fisiogest.terapias.domain.terapia import DatosTerapia, Terapia
from fisiogest.usuarios.domain.usuario import DatosUsuario, Rol, Usuario

pytestmark = pytest.mark.unit
HOY = date(2026, 10, 5)


def test_usuario_se_bloquea_tras_cinco_intentos_fallidos():
    usuario = Usuario("ana", "Ana", Rol.FISIOTERAPEUTA, "hash")
    ahora = datetime(2026, 10, 5, 8, 0)
    for _ in range(Usuario.MAX_INTENTOS):
        assert not usuario.esta_bloqueado(ahora)
        usuario.registrar_intento_fallido(ahora)
    assert usuario.esta_bloqueado(ahora)
    assert not usuario.esta_bloqueado(ahora + timedelta(minutes=Usuario.MINUTOS_BLOQUEO + 1))


@pytest.mark.parametrize("password", ["corta1", "sinnumeros", "12345678"])
def test_password_debil_es_rechazada(password):
    with pytest.raises(ValidationError) as error:
        Usuario.validar(DatosUsuario("nuevo", "Nuevo Usuario", "recepcionista", password))
    assert "password" in error.value.errores


def test_datos_de_usuario_validos_se_normalizan():
    username, nombre, rol = Usuario.validar(
        DatosUsuario(" Fisio.Maria ", "María  Pérez", "fisioterapeuta", "Segura2026")
    )
    assert (username, nombre, rol) == ("fisio.maria", "María Pérez", Rol.FISIOTERAPEUTA)


def datos_terapia(**cambios) -> DatosTerapia:
    base = {
        "fecha": "2026-10-05",
        "tipo": "Terapia manual",
        "zona_tratada": "Rodilla derecha",
        "dolor_inicial": "7",
        "dolor_final": "4",
        "procedimiento": "Movilización y ejercicios",
    }
    base.update(cambios)
    return DatosTerapia(**base)


def test_terapia_valida_calcula_mejora_del_dolor():
    terapia = Terapia.registrar(datos_terapia(), paciente_id=1, fisioterapeuta_id=2, hoy=HOY)
    assert terapia.mejora_dolor == 3


@pytest.mark.parametrize(
    "cambios, campo",
    [
        ({"dolor_inicial": "11"}, "dolor_inicial"),
        ({"dolor_final": "-1"}, "dolor_final"),
        ({"tipo": "Magia"}, "tipo"),
        ({"fecha": "2026-10-06"}, "fecha"),
        ({"procedimiento": "x"}, "procedimiento"),
        ({"zona_tratada": ""}, "zona_tratada"),
    ],
)
def test_validaciones_de_terapia(cambios, campo):
    with pytest.raises(ValidationError) as error:
        Terapia.registrar(datos_terapia(**cambios), paciente_id=1, fisioterapeuta_id=2, hoy=HOY)
    assert campo in error.value.errores


def test_periodo_de_reporte_valida_rango():
    assert Periodo.crear(date(2026, 1, 1), date(2026, 1, 31)).hasta == date(2026, 1, 31)
    with pytest.raises(ValidationError):
        Periodo.crear(date(2026, 2, 1), date(2026, 1, 1))
    with pytest.raises(ValidationError):
        Periodo.crear(date(2024, 1, 1), date(2026, 1, 1))
    with pytest.raises(ValidationError):
        Periodo.crear(None, date(2026, 1, 1))
