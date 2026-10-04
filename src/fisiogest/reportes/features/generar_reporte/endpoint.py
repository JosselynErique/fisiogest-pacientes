from flask import Blueprint, render_template, request

from fisiogest.reportes.features.generar_reporte.caso_uso import GenerarReporte
from fisiogest.shared.domain.errors import ValidationError
from fisiogest.shared.domain.validators import parsear_fecha
from fisiogest.shared.web.http import contenedor, requiere_rol
from fisiogest.usuarios.domain.usuario import Rol

bp = Blueprint("generar_reporte", __name__, template_folder="templates", url_prefix="/reportes")


@bp.get("/")
@requiere_rol(Rol.ADMINISTRADOR)
def ver():
    c = contenedor()
    hoy = c.reloj().date()
    datos = {
        "desde": request.args.get("desde") or hoy.replace(day=1).isoformat(),
        "hasta": request.args.get("hasta") or hoy.isoformat(),
    }
    try:
        reporte = GenerarReporte(c.reportes).ejecutar(
            parsear_fecha(datos["desde"]), parsear_fecha(datos["hasta"])
        )
    except ValidationError as error:
        return render_template(
            "reportes/ver.html", reporte=None, datos=datos, errores=error.errores
        ), 422
    return render_template("reportes/ver.html", reporte=reporte, datos=datos, errores={})
