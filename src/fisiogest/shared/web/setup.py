"""Configuración transversal de la aplicación web: sesión, seguridad, errores y plantillas."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time

from flask import Flask, g, redirect, render_template, request, session, url_for
from werkzeug.exceptions import HTTPException

from fisiogest.shared.web.http import contenedor, csrf_token, verificar_csrf
from fisiogest.usuarios.domain.usuario import Rol

ENDPOINTS_PUBLICOS = {"static", "salud", "iniciar_sesion.formulario", "iniciar_sesion.ingresar"}


@dataclass(frozen=True)
class ItemMenu:
    etiqueta: str
    endpoint: str
    roles: tuple[Rol, ...]


MENU = (
    ItemMenu("Inicio", "panel.ver", tuple(Rol)),
    ItemMenu("Pacientes", "listar_pacientes.listar", tuple(Rol)),
    ItemMenu("Agenda", "consultar_agenda.ver", tuple(Rol)),
    ItemMenu("Reportes", "generar_reporte.ver", (Rol.ADMINISTRADOR,)),
    ItemMenu("Usuarios", "listar_usuarios.listar", (Rol.ADMINISTRADOR,)),
)


def _fecha(valor: date | datetime | None) -> str:
    return valor.strftime("%d/%m/%Y") if valor else "—"


def _hora(valor: time | datetime | None) -> str:
    return valor.strftime("%H:%M") if valor else "—"


def configurar_web(app: Flask) -> None:
    @app.before_request
    def cargar_sesion_y_proteger():
        g.usuario = None
        usuario_id = session.get("usuario_id")
        if usuario_id is not None:
            usuario = contenedor().usuarios.obtener(usuario_id)
            if usuario and usuario.activo:
                g.usuario = usuario
            else:
                session.clear()
        verificar_csrf()
        if request.endpoint not in ENDPOINTS_PUBLICOS and g.usuario is None:
            return redirect(url_for("iniciar_sesion.formulario", next=request.path))
        return None

    @app.after_request
    def cabeceras_de_seguridad(respuesta):
        respuesta.headers.setdefault("X-Content-Type-Options", "nosniff")
        respuesta.headers.setdefault("X-Frame-Options", "DENY")
        respuesta.headers.setdefault("Referrer-Policy", "same-origin")
        respuesta.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'",
        )
        return respuesta

    @app.context_processor
    def contexto_global():
        usuario = g.get("usuario")
        menu = [
            item
            for item in MENU
            if usuario and usuario.rol in item.roles and item.endpoint in app.view_functions
        ]
        return {"usuario": usuario, "menu": menu, "Rol": Rol}

    app.jinja_env.globals["csrf_token"] = csrf_token
    app.add_template_filter(_fecha, "fecha")
    app.add_template_filter(_hora, "hora")

    @app.errorhandler(HTTPException)
    def error_http(error: HTTPException):
        titulos = {
            400: "Solicitud inválida",
            403: "Acceso denegado",
            404: "No encontrado",
            405: "Método no permitido",
        }
        return (
            render_template(
                "error.html",
                codigo=error.code,
                titulo=titulos.get(error.code or 500, "Error"),
                mensaje=error.description,
            ),
            error.code,
        )

    @app.get("/salud")
    def salud():
        return {"estado": "ok", "aplicacion": "FisioGest"}
