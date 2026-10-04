"""Fábrica de la aplicación Flask (adaptador de entrada HTTP)."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta
from pathlib import Path

from flask import Flask

from fisiogest.config import Config
from fisiogest.container import construir_contenedor
from fisiogest.modulos import SLICES
from fisiogest.shared.infrastructure.seed import cargar_datos_iniciales
from fisiogest.shared.web.setup import configurar_web

_WEB = Path(__file__).parent / "shared" / "web"


def create_app(config: Config | None = None, reloj: Callable[[], datetime] = datetime.now) -> Flask:
    config = config or Config.desde_entorno()
    app = Flask(
        __name__,
        template_folder=str(_WEB / "templates"),
        static_folder=str(_WEB / "static"),
    )
    app.config.update(
        SECRET_KEY=config.secret_key,
        TESTING=config.testing,
        FISIOGEST_DEMO=config.demo,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
    )

    contenedor = construir_contenedor(config, reloj)
    contenedor.db.inicializar()
    cargar_datos_iniciales(contenedor, demo=config.demo)
    app.extensions["fisiogest"] = contenedor

    for blueprint in SLICES:
        app.register_blueprint(blueprint)
    configurar_web(app)
    return app
