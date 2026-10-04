from flask import Blueprint, render_template

from fisiogest.shared.web.http import contenedor, requiere_rol
from fisiogest.usuarios.domain.usuario import Rol
from fisiogest.usuarios.features.listar_usuarios.caso_uso import ListarUsuarios

bp = Blueprint("listar_usuarios", __name__, template_folder="templates", url_prefix="/usuarios")


@bp.get("/")
@requiere_rol(Rol.ADMINISTRADOR)
def listar():
    usuarios = ListarUsuarios(contenedor().usuarios).ejecutar()
    return render_template("usuarios/listar.html", usuarios=usuarios)
