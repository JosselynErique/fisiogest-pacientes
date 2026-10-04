from flask import Blueprint, render_template, request

from fisiogest.pacientes.features.listar_pacientes.caso_uso import ListarPacientes
from fisiogest.shared.web.http import contenedor, requiere_rol

bp = Blueprint("listar_pacientes", __name__, template_folder="templates", url_prefix="/pacientes")


@bp.get("/")
@requiere_rol()
def listar():
    texto = request.args.get("q", "")
    incluir_inactivos = request.args.get("inactivos") == "1"
    pacientes = ListarPacientes(contenedor().pacientes).ejecutar(texto, incluir_inactivos)
    return render_template(
        "pacientes/listar.html",
        pacientes=pacientes,
        q=texto,
        incluir_inactivos=incluir_inactivos,
    )
