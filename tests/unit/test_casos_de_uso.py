"""Casos de uso probados con adaptadores en memoria (sin SQLite ni Flask)."""

from datetime import date, datetime

import pytest

from fakes import (
    CitasEnMemoria,
    HasherFalso,
    PacientesEnMemoria,
    TerapiasEnMemoria,
    UsuariosEnMemoria,
)
from fisiogest.citas.domain.cita import DatosCita, EstadoCita
from fisiogest.citas.features.agendar_cita.caso_uso import AgendarCita
from fisiogest.citas.features.cancelar_cita.caso_uso import CancelarCita
from fisiogest.citas.features.consultar_agenda.caso_uso import ConsultarAgenda
from fisiogest.historial.features.consultar_historial.caso_uso import ConsultarHistorial
from fisiogest.pacientes.domain.paciente import DatosPaciente
from fisiogest.pacientes.features.actualizar_paciente.caso_uso import ActualizarPaciente
from fisiogest.pacientes.features.dar_de_baja_paciente.caso_uso import DarDeBajaPaciente
from fisiogest.pacientes.features.listar_pacientes.caso_uso import ListarPacientes
from fisiogest.pacientes.features.registrar_paciente.caso_uso import RegistrarPaciente
from fisiogest.shared.domain.errors import (
    AuthenticationError,
    ConflictError,
    DomainError,
    NotFoundError,
    ValidationError,
)
from fisiogest.terapias.domain.terapia import DatosTerapia
from fisiogest.terapias.features.registrar_terapia.caso_uso import RegistrarTerapia
from fisiogest.usuarios.domain.usuario import DatosUsuario, Rol, Usuario
from fisiogest.usuarios.features.cambiar_estado_usuario.caso_uso import CambiarEstadoUsuario
from fisiogest.usuarios.features.iniciar_sesion.caso_uso import IniciarSesion
from fisiogest.usuarios.features.registrar_usuario.caso_uso import RegistrarUsuario
from helpers import CEDULA_1, CEDULA_2

pytestmark = pytest.mark.unit
AHORA = datetime(2026, 10, 5, 8, 0)
HOY = "2026-10-05"


@pytest.fixture
def repos():
    usuarios = UsuariosEnMemoria()
    hasher = HasherFalso()
    admin = usuarios.guardar(
        Usuario("admin", "Admin", Rol.ADMINISTRADOR, hasher.hashear("Clave2026"))
    )
    ana = usuarios.guardar(Usuario("ana", "Ana", Rol.FISIOTERAPEUTA, hasher.hashear("Clave2026")))
    luis = usuarios.guardar(
        Usuario("luis", "Luis", Rol.FISIOTERAPEUTA, hasher.hashear("Clave2026"))
    )
    recep = usuarios.guardar(
        Usuario("rosa", "Rosa", Rol.RECEPCIONISTA, hasher.hashear("Clave2026"))
    )
    pacientes = PacientesEnMemoria()
    p1 = RegistrarPaciente(pacientes).ejecutar(DatosPaciente(CEDULA_1, "Ana", "Mora"))
    p2 = RegistrarPaciente(pacientes).ejecutar(DatosPaciente(CEDULA_2, "Jorge", "Vera"))
    return {
        "usuarios": usuarios,
        "hasher": hasher,
        "pacientes": pacientes,
        "citas": CitasEnMemoria(),
        "terapias": TerapiasEnMemoria(),
        "admin": admin,
        "ana": ana,
        "luis": luis,
        "recep": recep,
        "p1": p1,
        "p2": p2,
    }


def agendar(r, paciente, fisio, hora="10:00", fecha="2026-10-06"):
    caso = AgendarCita(r["citas"], r["pacientes"], r["usuarios"], lambda: AHORA)
    return caso.ejecutar(DatosCita(paciente.id, fisio.id, fecha, hora, "45", "Dolor lumbar"))


# --- Pacientes -------------------------------------------------------------------------


def test_rf01_no_permite_cedula_duplicada(repos):
    with pytest.raises(ConflictError):
        RegistrarPaciente(repos["pacientes"]).ejecutar(DatosPaciente(CEDULA_1, "Otra", "Persona"))


def test_rf02_actualizar_y_evitar_cedula_de_otro_paciente(repos):
    caso = ActualizarPaciente(repos["pacientes"])
    actualizado = caso.ejecutar(repos["p1"].id, DatosPaciente(CEDULA_1, "Ana Lucía", "Mora"))
    assert actualizado.nombres == "Ana Lucía"
    with pytest.raises(ConflictError):
        caso.ejecutar(repos["p1"].id, DatosPaciente(CEDULA_2, "Ana", "Mora"))
    with pytest.raises(NotFoundError):
        caso.ejecutar(999, DatosPaciente(CEDULA_1, "Ana", "Mora"))


def test_rf03_baja_logica_oculta_al_paciente_del_listado(repos):
    DarDeBajaPaciente(repos["pacientes"]).ejecutar(repos["p1"].id)
    listar = ListarPacientes(repos["pacientes"])
    assert [p.id for p in listar.ejecutar()] == [repos["p2"].id]
    assert len(listar.ejecutar(incluir_inactivos=True)) == 2


# --- Citas -----------------------------------------------------------------------------


def test_rf04_agendar_cita(repos):
    cita = agendar(repos, repos["p1"], repos["ana"])
    assert cita.id is not None and cita.estado is EstadoCita.PROGRAMADA


def test_rf05_rechaza_cruce_de_horario_del_fisioterapeuta(repos):
    agendar(repos, repos["p1"], repos["ana"], "10:00")
    with pytest.raises(ConflictError, match="Ana ya tiene una cita"):
        agendar(repos, repos["p2"], repos["ana"], "10:30")
    # Otro fisioterapeuta sí puede atender a esa hora
    assert agendar(repos, repos["p2"], repos["luis"], "10:30").id


def test_rf05_rechaza_que_el_paciente_tenga_dos_citas_a_la_vez(repos):
    agendar(repos, repos["p1"], repos["ana"], "10:00")
    with pytest.raises(ConflictError, match="El paciente ya tiene otra cita"):
        agendar(repos, repos["p1"], repos["luis"], "10:15")


def test_agendar_valida_paciente_activo_y_rol_fisioterapeuta(repos):
    DarDeBajaPaciente(repos["pacientes"]).ejecutar(repos["p2"].id)
    with pytest.raises(ValidationError) as error:
        agendar(repos, repos["p2"], repos["recep"])
    assert {"paciente_id", "fisioterapeuta_id"} <= set(error.value.errores)


def test_rf10_cancelar_libera_el_horario(repos):
    cita = agendar(repos, repos["p1"], repos["ana"], "10:00")
    CancelarCita(repos["citas"]).ejecutar(cita.id, "Paciente con fiebre")
    assert agendar(repos, repos["p2"], repos["ana"], "10:00").id


def test_fisioterapeuta_solo_ve_su_agenda(repos):
    agendar(repos, repos["p1"], repos["ana"], "10:00")
    agendar(repos, repos["p2"], repos["luis"], "10:00")
    caso = ConsultarAgenda(repos["citas"])
    assert len(caso.ejecutar(date(2026, 10, 6), repos["ana"]).citas) == 1
    assert len(caso.ejecutar(date(2026, 10, 6), repos["recep"]).citas) == 2


# --- Terapias e historial ---------------------------------------------------------------


DATOS_SESION = DatosTerapia(
    fecha="2026-10-05",
    tipo="Terapia manual",
    zona_tratada="Zona lumbar",
    dolor_inicial=7,
    dolor_final=4,
    procedimiento="Movilización lumbar y estiramientos",
)


def test_rf06_registrar_sesion_desde_cita_la_marca_atendida(repos):
    cita = agendar(repos, repos["p1"], repos["ana"], fecha=HOY)
    caso = RegistrarTerapia(repos["terapias"], repos["pacientes"], repos["citas"], lambda: AHORA)
    terapia = caso.desde_cita(cita.id, DATOS_SESION, repos["ana"])
    assert terapia.cita_id == cita.id
    assert repos["citas"].obtener(cita.id).estado is EstadoCita.ATENDIDA


def test_rf06_solo_el_fisioterapeuta_asignado_atiende(repos):
    cita = agendar(repos, repos["p1"], repos["ana"], fecha=HOY)
    caso = RegistrarTerapia(repos["terapias"], repos["pacientes"], repos["citas"], lambda: AHORA)
    with pytest.raises(DomainError):
        caso.desde_cita(cita.id, DATOS_SESION, repos["luis"])


def test_no_se_puede_atender_una_cita_futura(repos):
    cita = agendar(repos, repos["p1"], repos["ana"], fecha="2026-10-07")
    caso = RegistrarTerapia(repos["terapias"], repos["pacientes"], repos["citas"], lambda: AHORA)
    with pytest.raises(DomainError, match="del día"):
        caso.desde_cita(cita.id, DATOS_SESION, repos["ana"])


def test_rf07_historial_consolida_citas_sesiones_y_evolucion(repos):
    cita = agendar(repos, repos["p1"], repos["ana"], fecha=HOY)
    caso = RegistrarTerapia(repos["terapias"], repos["pacientes"], repos["citas"], lambda: AHORA)
    caso.desde_cita(cita.id, DATOS_SESION, repos["ana"])
    caso.sin_cita(repos["p1"].id, DATOS_SESION, repos["ana"])
    historial = ConsultarHistorial(
        repos["pacientes"], repos["citas"], repos["terapias"], lambda: AHORA
    ).ejecutar(repos["p1"].id)
    assert historial.total_sesiones == 2
    assert len(historial.citas) == 1
    assert historial.evolucion_dolor == (7, 4)


# --- Usuarios --------------------------------------------------------------------------


def test_rf09_inicio_de_sesion_y_bloqueo(repos):
    caso = IniciarSesion(repos["usuarios"], repos["hasher"], lambda: AHORA)
    assert caso.ejecutar("ANA", "Clave2026").username == "ana"
    for _ in range(Usuario.MAX_INTENTOS):
        with pytest.raises(AuthenticationError, match="incorrectos"):
            caso.ejecutar("ana", "equivocada")
    with pytest.raises(AuthenticationError, match="bloqueada"):
        caso.ejecutar("ana", "Clave2026")


def test_usuario_inexistente_recibe_mensaje_generico(repos):
    caso = IniciarSesion(repos["usuarios"], repos["hasher"], lambda: AHORA)
    with pytest.raises(AuthenticationError, match="Usuario o contraseña incorrectos"):
        caso.ejecutar("nadie", "Clave2026")


def test_registrar_usuario_cifra_password_y_evita_duplicados(repos):
    caso = RegistrarUsuario(repos["usuarios"], repos["hasher"])
    nuevo = caso.ejecutar(DatosUsuario("fisio.eva", "Eva Paz", "fisioterapeuta", "Segura2026"))
    assert nuevo.password_hash != "Segura2026"
    with pytest.raises(ConflictError):
        caso.ejecutar(DatosUsuario("fisio.eva", "Eva Paz", "fisioterapeuta", "Segura2026"))


def test_no_se_puede_desactivar_al_ultimo_administrador_ni_a_si_mismo(repos):
    caso = CambiarEstadoUsuario(repos["usuarios"])
    with pytest.raises(DomainError, match="propia cuenta"):
        caso.ejecutar(repos["admin"].id, False, repos["admin"].id)
    with pytest.raises(DomainError, match="al menos un administrador"):
        caso.ejecutar(repos["admin"].id, False, repos["recep"].id)
    assert not caso.ejecutar(repos["ana"].id, False, repos["admin"].id).activo
