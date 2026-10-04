from flask import Blueprint, abort, render_template

from fisiogest.historial.features.consultar_historial.caso_uso import ConsultarHistorial
from fisiogest.shared.domain.errors import NotFoundError
from fisiogest.shared.web.http import contenedor, requiere_rol

bp = Blueprint(
    "consultar_historial", __name__, template_folder="templates", url_prefix="/pacientes"
)


@bp.get("/<int:paciente_id>")
@requiere_rol()
def ver(paciente_id: int):
    c = contenedor()
    try:
        historial = ConsultarHistorial(c.pacientes, c.citas, c.terapias, c.reloj).ejecutar(
            paciente_id
        )
    except NotFoundError:
        abort(404)
    return render_template("historial/ver.html", h=historial, p=historial.paciente)
