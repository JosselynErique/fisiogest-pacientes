from flask import Blueprint, abort, flash, redirect, url_for

from fisiogest.pacientes.features.dar_de_baja_paciente.caso_uso import DarDeBajaPaciente
from fisiogest.shared.domain.errors import DomainError, NotFoundError
from fisiogest.shared.web.http import contenedor, requiere_rol
from fisiogest.usuarios.domain.usuario import Rol

bp = Blueprint("dar_de_baja_paciente", __name__, url_prefix="/pacientes")

ROLES = (Rol.ADMINISTRADOR, Rol.RECEPCIONISTA)


@bp.post("/<int:paciente_id>/baja")
@requiere_rol(*ROLES)
def dar_de_baja(paciente_id: int):
    try:
        paciente = DarDeBajaPaciente(contenedor().pacientes).ejecutar(paciente_id)
    except NotFoundError:
        abort(404)
    except DomainError as error:
        flash(str(error), "error")
    else:
        flash(f"{paciente.nombre_completo} fue dado de baja. Su historial se conserva.", "aviso")
    return redirect(url_for("consultar_historial.ver", paciente_id=paciente_id))


@bp.post("/<int:paciente_id>/reactivar")
@requiere_rol(*ROLES)
def reactivar(paciente_id: int):
    try:
        paciente = DarDeBajaPaciente(contenedor().pacientes).reactivar(paciente_id)
    except NotFoundError:
        abort(404)
    except DomainError as error:
        flash(str(error), "error")
    else:
        flash(f"{paciente.nombre_completo} fue reactivado.", "exito")
    return redirect(url_for("consultar_historial.ver", paciente_id=paciente_id))
