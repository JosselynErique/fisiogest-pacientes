from flask import Blueprint, abort, flash, redirect, request, url_for

from fisiogest.shared.domain.errors import DomainError, NotFoundError
from fisiogest.shared.web.http import contenedor, requiere_rol, usuario_actual
from fisiogest.usuarios.domain.usuario import Rol
from fisiogest.usuarios.features.cambiar_estado_usuario.caso_uso import CambiarEstadoUsuario

bp = Blueprint("cambiar_estado_usuario", __name__, url_prefix="/usuarios")


@bp.post("/<int:usuario_id>/estado")
@requiere_rol(Rol.ADMINISTRADOR)
def cambiar(usuario_id: int):
    activo = request.form.get("activo") == "1"
    try:
        usuario = CambiarEstadoUsuario(contenedor().usuarios).ejecutar(
            usuario_id, activo, usuario_actual().id
        )
    except NotFoundError:
        abort(404)
    except DomainError as error:
        flash(str(error), "error")
    else:
        estado = "activada" if usuario.activo else "desactivada"
        flash(f"Cuenta de {usuario.nombre_completo} {estado}.", "exito")
    return redirect(url_for("listar_usuarios.listar"))
