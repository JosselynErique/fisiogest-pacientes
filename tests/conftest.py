from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest

from fisiogest.app import create_app
from fisiogest.config import Config
from fisiogest.usuarios.domain.usuario import Rol, Usuario
from helpers import AHORA, PASSWORD, iniciar_sesion, obtener_csrf


@pytest.fixture
def ahora() -> datetime:
    return AHORA


@pytest.fixture
def app(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("FISIOGEST_ADMIN_PASSWORD", PASSWORD)
    config = Config(
        secret_key="clave-de-pruebas",
        database=tmp_path / "fisiogest_test.db",
        demo=False,
        testing=True,
    )
    aplicacion = create_app(config, reloj=lambda: AHORA)
    c = aplicacion.extensions["fisiogest"]
    for username, nombre, rol in (
        ("recepcion", "Rosa Recepción", Rol.RECEPCIONISTA),
        ("fisio.ana", "Ana Fisio", Rol.FISIOTERAPEUTA),
        ("fisio.luis", "Luis Fisio", Rol.FISIOTERAPEUTA),
    ):
        c.usuarios.guardar(Usuario(username, nombre, rol, c.hasher.hashear(PASSWORD)))
    return aplicacion


@pytest.fixture
def contenedor(app):
    return app.extensions["fisiogest"]


@pytest.fixture
def cliente(app):
    return app.test_client()


@pytest.fixture
def como(app):
    """Devuelve un cliente HTTP con sesión iniciada para el usuario indicado."""

    def _como(username: str):
        cliente = app.test_client()
        respuesta = iniciar_sesion(cliente, username)
        assert respuesta.status_code == 302, "no se pudo iniciar sesión en la prueba"
        cliente.csrf = obtener_csrf(cliente)
        return cliente

    return _como
