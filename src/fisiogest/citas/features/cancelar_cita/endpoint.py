from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from fisiogest.citas.features.cancelar_cita.caso_uso import CancelarCita
from fisiogest.shared.domain.errors import DomainError, NotFoundError, ValidationError
from fisiogest.shared.web.http import contenedor, requiere_rol
from fisiogest.usuarios.domain.usuario import Rol

bp = Blueprint("cancelar_cita", __name__, template_folder="templates", url_prefix="/citas")

ROLES = (Rol.ADMINISTRADOR, Rol.RECEPCIONISTA)


@bp.get("/<int:cita_id>/cancelar")
@requiere_rol(*ROLES)
def confirmar(cita_id: int):
    try:
        detalle = CancelarCita(contenedor().citas).detalle(cita_id)
    except NotFoundError:
        abort(404)
    return render_template("citas/cancelar.html", detalle=detalle, datos={}, errores={})


@bp.post("/<int:cita_id>/cancelar")
@requiere_rol(*ROLES)
def cancelar(cita_id: int):
    caso_uso = CancelarCita(contenedor().citas)
    motivo = request.form.get("motivo_cancelacion", "")
    try:
        cita = caso_uso.ejecutar(cita_id, motivo)
    except NotFoundError:
        abort(404)
    except ValidationError as error:
        detalle = caso_uso.detalle(cita_id)
        datos = {"motivo_cancelacion": motivo}
        return render_template(
            "citas/cancelar.html", detalle=detalle, datos=datos, errores=error.errores
        ), 422
    except DomainError as error:
        flash(str(error), "error")
        return redirect(url_for("consultar_agenda.ver"))
    flash("La cita fue cancelada y el horario quedó libre.", "aviso")
    return redirect(url_for("consultar_agenda.ver", fecha=cita.fecha.isoformat()))
