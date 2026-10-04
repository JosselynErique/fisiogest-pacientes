"""Integración del adaptador HTTP (Flask) con los casos de uso y SQLite."""

import pytest

from helpers import CEDULA_1, CEDULA_2, PASSWORD, iniciar_sesion

pytestmark = pytest.mark.integration

DATOS_PACIENTE = {
    "cedula": CEDULA_1,
    "nombres": "Sofia",
    "apellidos": "Robayo",
    "telefono": "0999999999",
    "direccion": "Loja",
    "correo": "sofia@gmail.com",
}


def test_cp04_registrar_paciente_correctamente(como, contenedor):
    """Caso crítico del plan de pruebas: el formulario llega a Flask y se guarda el paciente."""
    cliente = como("recepcion")
    respuesta = cliente.post(
        "/pacientes/nuevo", data={**DATOS_PACIENTE, "_csrf": cliente.csrf}, follow_redirects=True
    )
    assert respuesta.status_code == 200
    assert b"Paciente Sofia Robayo registrado correctamente" in respuesta.data
    assert contenedor.pacientes.obtener_por_cedula(CEDULA_1) is not None


def test_cp05_consultar_pacientes_muestra_el_registro(como):
    cliente = como("recepcion")
    cliente.post("/pacientes/nuevo", data={**DATOS_PACIENTE, "_csrf": cliente.csrf})
    respuesta = cliente.get("/pacientes/?q=robayo")
    assert respuesta.status_code == 200
    assert CEDULA_1.encode() in respuesta.data


def test_formulario_invalido_muestra_errores_sin_guardar(como, contenedor):
    cliente = como("recepcion")
    respuesta = cliente.post(
        "/pacientes/nuevo",
        data={**DATOS_PACIENTE, "cedula": "1234567890", "nombres": "", "_csrf": cliente.csrf},
    )
    assert respuesta.status_code == 422
    assert "La cédula ecuatoriana no es válida".encode() in respuesta.data
    assert b"Los nombres son obligatorios" in respuesta.data
    assert contenedor.pacientes.contar() == 0


def test_cedula_duplicada_devuelve_conflicto(como):
    cliente = como("recepcion")
    cliente.post("/pacientes/nuevo", data={**DATOS_PACIENTE, "_csrf": cliente.csrf})
    respuesta = cliente.post("/pacientes/nuevo", data={**DATOS_PACIENTE, "_csrf": cliente.csrf})
    assert respuesta.status_code == 409


def test_editar_y_dar_de_baja_paciente(como, contenedor):
    cliente = como("recepcion")
    cliente.post("/pacientes/nuevo", data={**DATOS_PACIENTE, "_csrf": cliente.csrf})
    paciente = contenedor.pacientes.obtener_por_cedula(CEDULA_1)

    cliente.post(
        f"/pacientes/{paciente.id}/editar",
        data={**DATOS_PACIENTE, "telefono": "0981234567", "_csrf": cliente.csrf},
    )
    assert contenedor.pacientes.obtener(paciente.id).telefono == "0981234567"

    cliente.post(f"/pacientes/{paciente.id}/baja", data={"_csrf": cliente.csrf})
    assert not contenedor.pacientes.obtener(paciente.id).activo
    assert CEDULA_1.encode() not in cliente.get("/pacientes/").data


def test_rf05_agendar_en_horario_ocupado_responde_409(como, contenedor):
    cliente = como("recepcion")
    for cedula in (CEDULA_1, CEDULA_2):
        cliente.post(
            "/pacientes/nuevo", data={**DATOS_PACIENTE, "cedula": cedula, "_csrf": cliente.csrf}
        )
    p1, p2 = (contenedor.pacientes.obtener_por_cedula(c) for c in (CEDULA_1, CEDULA_2))
    fisio = contenedor.usuarios.obtener_por_username("fisio.ana")
    cita = {
        "fisioterapeuta_id": fisio.id,
        "fecha": "2026-10-06",
        "hora_inicio": "10:00",
        "duracion_minutos": "45",
    }

    primera = cliente.post(
        "/citas/nueva", data={**cita, "paciente_id": p1.id, "_csrf": cliente.csrf}
    )
    assert primera.status_code == 302
    segunda = cliente.post(
        "/citas/nueva", data={**cita, "paciente_id": p2.id, "_csrf": cliente.csrf}
    )
    assert segunda.status_code == 409
    assert b"Ana Fisio ya tiene una cita" in segunda.data


# --- Seguridad (RNF-02) -------------------------------------------------------------------


def test_rutas_protegidas_redirigen_al_login(cliente):
    respuesta = cliente.get("/pacientes/")
    assert respuesta.status_code == 302
    assert "/login" in respuesta.location


def test_login_incorrecto_no_revela_si_el_usuario_existe(cliente):
    respuesta = iniciar_sesion(cliente, "recepcion", "incorrecta")
    assert respuesta.status_code == 401
    assert "Usuario o contraseña incorrectos".encode() in respuesta.data


def test_post_sin_token_csrf_es_rechazado(como):
    cliente = como("recepcion")
    respuesta = cliente.post("/pacientes/nuevo", data=DATOS_PACIENTE)
    assert respuesta.status_code == 400


@pytest.mark.parametrize(
    "usuario, ruta, esperado",
    [
        ("recepcion", "/usuarios/", 403),
        ("recepcion", "/reportes/", 403),
        ("fisio.ana", "/pacientes/nuevo", 403),
        ("fisio.ana", "/citas/nueva", 403),
        ("admin", "/usuarios/", 200),
        ("admin", "/reportes/", 200),
    ],
)
def test_permisos_por_rol(como, usuario, ruta, esperado):
    assert como(usuario).get(ruta).status_code == esperado


def test_cabeceras_de_seguridad(cliente):
    respuesta = cliente.get("/login")
    assert respuesta.headers["X-Frame-Options"] == "DENY"
    assert "default-src 'self'" in respuesta.headers["Content-Security-Policy"]


def test_cerrar_sesion(como):
    cliente = como("admin")
    cliente.post("/logout", data={"_csrf": cliente.csrf})
    assert cliente.get("/").status_code == 302


def test_administrador_crea_usuario_que_puede_ingresar(como, cliente):
    admin = como("admin")
    respuesta = admin.post(
        "/usuarios/nuevo",
        data={
            "username": "fisio.eva",
            "nombre_completo": "Eva Paz",
            "rol": "fisioterapeuta",
            "password": "Segura2026",
            "_csrf": admin.csrf,
        },
    )
    assert respuesta.status_code == 302
    assert iniciar_sesion(cliente, "fisio.eva", "Segura2026").status_code == 302
    assert iniciar_sesion(cliente.application.test_client(), "admin", PASSWORD).status_code == 302


def test_salud(cliente):
    assert cliente.get("/salud").json == {"estado": "ok", "aplicacion": "FisioGest"}
