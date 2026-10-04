"""Utilidades del adaptador HTTP compartidas por todas las slices."""

from __future__ import annotations

import secrets
from collections.abc import Callable
from functools import wraps
from typing import TYPE_CHECKING, Any, TypeVar

from flask import abort, current_app, g, redirect, request, session, url_for

if TYPE_CHECKING:
    from fisiogest.container import Container
    from fisiogest.usuarios.domain.usuario import Rol, Usuario

F = TypeVar("F", bound=Callable[..., Any])
CSRF_CLAVE = "_csrf"


def contenedor() -> Container:
    """Devuelve el contenedor de dependencias armado en la raíz de composición."""
    return current_app.extensions["fisiogest"]


def usuario_actual() -> Usuario:
    return g.usuario


def formulario() -> dict[str, str]:
    return {clave: valor for clave, valor in request.form.items() if clave != CSRF_CLAVE}


def csrf_token() -> str:
    token = session.get(CSRF_CLAVE)
    if not token:
        token = secrets.token_urlsafe(32)
        session[CSRF_CLAVE] = token
    return token


def verificar_csrf() -> None:
    if request.method not in ("POST", "PUT", "PATCH", "DELETE"):
        return
    enviado = request.form.get(CSRF_CLAVE) or request.headers.get("X-CSRF-Token", "")
    esperado = session.get(CSRF_CLAVE, "")
    if not enviado or not esperado or not secrets.compare_digest(enviado, esperado):
        abort(
            400,
            description="La sesión del formulario expiró. Recargue la página e intente de nuevo.",
        )


def requiere_rol(*roles: Rol) -> Callable[[F], F]:
    """Restringe una ruta a ciertos roles (RF-09). Sin roles: solo exige sesión iniciada."""

    def decorador(vista: F) -> F:
        @wraps(vista)
        def envoltura(*args: Any, **kwargs: Any) -> Any:
            if g.get("usuario") is None:
                return redirect(url_for("iniciar_sesion.formulario", next=request.path))
            if roles and g.usuario.rol not in roles:
                abort(403)
            return vista(*args, **kwargs)

        return envoltura  # type: ignore[return-value]

    return decorador


def destino_seguro(destino: str | None, por_defecto: str) -> str:
    """Evita redirecciones abiertas: solo se aceptan rutas internas."""
    if destino and destino.startswith("/") and not destino.startswith("//"):
        return destino
    return por_defecto
