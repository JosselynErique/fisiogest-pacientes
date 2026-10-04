from datetime import timedelta

from flask import Blueprint, render_template, request

from fisiogest.citas.features.consultar_agenda.caso_uso import ConsultarAgenda
from fisiogest.shared.domain.validators import parsear_entero, parsear_fecha
from fisiogest.shared.web.http import contenedor, requiere_rol, usuario_actual
from fisiogest.usuarios.domain.usuario import Rol

bp = Blueprint("consultar_agenda", __name__, template_folder="templates", url_prefix="/citas")


@bp.get("/")
@requiere_rol()
def ver():
    c = contenedor()
    hoy = c.reloj().date()
    fecha = parsear_fecha(request.args.get("fecha", "")) or hoy
    fisio_id = parsear_entero(request.args.get("fisioterapeuta_id"))
    agenda = ConsultarAgenda(c.citas).ejecutar(fecha, usuario_actual(), fisio_id)
    fisios = c.usuarios.listar(Rol.FISIOTERAPEUTA, solo_activos=True)
    return render_template(
        "citas/agenda.html",
        agenda=agenda,
        hoy=hoy,
        anterior=fecha - timedelta(days=1),
        siguiente=fecha + timedelta(days=1),
        fisios=fisios,
        fisio_id=fisio_id,
    )
