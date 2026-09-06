import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from app import app


def test_registrar_paciente_correctamente():
    cliente = app.test_client()

    datos = {
        "cedula": "1104567890",
        "nombres": "Sofia",
        "apellidos": "Robayo",
        "telefono": "0999999999",
        "direccion": "Loja",
        "correo": "sofia@gmail.com"
    }

    respuesta = cliente.post("/registrar", data=datos)

    assert respuesta.status_code == 200
    assert b"Paciente registrado correctamente" in respuesta.data