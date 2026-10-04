from flask import Blueprint, flash, redirect, render_template, url_for

from fisiogest.shared.domain.errors import ConflictError, ValidationError
from fisiogest.shared.web.http import contenedor, formulario, requiere_rol
from fisiogest.usuarios.domain.usuario import DatosUsuario, Rol
from fisiogest.usuarios.features.registrar_usuario.caso_uso import RegistrarUsuario

bp = Blueprint("registrar_usuario", __name__, template_folder="templates", url_prefix="/usuarios")

ROLES = [(rol.value, rol.etiqueta) for rol in Rol]


@bp.get("/nuevo")
@requiere_rol(Rol.ADMINISTRADOR)
def formulario_nuevo():
    return render_template("usuarios/registrar.html", datos={}, errores={}, roles=ROLES)


@bp.post("/nuevo")
@requiere_rol(Rol.ADMINISTRADOR)
def registrar():
    datos = formulario()
    c = contenedor()
    try:
        usuario = RegistrarUsuario(c.usuarios, c.hasher).ejecutar(
            DatosUsuario(
                username=datos.get("username", ""),
                nombre_completo=datos.get("nombre_completo", ""),
                rol=datos.get("rol", ""),
                password=datos.get("password", ""),
            )
        )
    except ValidationError as error:
        datos.pop("password", None)
        return (
            render_template(
                "usuarios/registrar.html", datos=datos, errores=error.errores, roles=ROLES
            ),
            422,
        )
    except ConflictError as error:
        datos.pop("password", None)
        errores = {"username": str(error)}
        return (
            render_template("usuarios/registrar.html", datos=datos, errores=errores, roles=ROLES),
            409,
        )
    flash(f"Usuario «{usuario.username}» creado como {usuario.rol.etiqueta}.", "exito")
    return redirect(url_for("listar_usuarios.listar"))
