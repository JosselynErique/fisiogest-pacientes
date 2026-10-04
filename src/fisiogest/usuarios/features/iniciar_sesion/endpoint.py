from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from fisiogest.shared.domain.errors import AuthenticationError
from fisiogest.shared.web.http import contenedor, destino_seguro
from fisiogest.usuarios.features.iniciar_sesion.caso_uso import IniciarSesion

bp = Blueprint("iniciar_sesion", __name__, template_folder="templates")


def _caso_uso() -> IniciarSesion:
    c = contenedor()
    return IniciarSesion(c.usuarios, c.hasher, c.reloj)


@bp.get("/login")
def formulario():
    if session.get("usuario_id"):
        return redirect(url_for("panel.ver"))
    return render_template(
        "usuarios/iniciar_sesion.html", demo=current_app.config.get("FISIOGEST_DEMO", False)
    )


@bp.post("/login")
def ingresar():
    username = request.form.get("username", "")
    try:
        usuario = _caso_uso().ejecutar(username, request.form.get("password", ""))
    except AuthenticationError as error:
        flash(str(error), "error")
        return (
            render_template(
                "usuarios/iniciar_sesion.html",
                username=username,
                demo=current_app.config.get("FISIOGEST_DEMO", False),
            ),
            401,
        )
    session.clear()
    session.permanent = True
    session["usuario_id"] = usuario.id
    flash(f"Bienvenido/a, {usuario.nombre_completo}.", "exito")
    return redirect(destino_seguro(request.args.get("next"), url_for("panel.ver")))


@bp.post("/logout")
def salir():
    session.clear()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("iniciar_sesion.formulario"))
