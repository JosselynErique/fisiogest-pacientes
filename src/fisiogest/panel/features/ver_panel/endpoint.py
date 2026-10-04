from flask import Blueprint, render_template

from fisiogest.panel.features.ver_panel.caso_uso import VerPanel
from fisiogest.shared.web.http import contenedor, requiere_rol, usuario_actual

bp = Blueprint("panel", __name__, template_folder="templates")


@bp.get("/")
@requiere_rol()
def ver():
    c = contenedor()
    resumen = VerPanel(c.pacientes, c.citas, c.reportes, c.reloj).ejecutar(usuario_actual())
    return render_template("panel/ver.html", r=resumen, hoy=c.reloj().date())
