from dataclasses import fields

from flask import Blueprint, abort, flash, redirect, render_template, url_for

from fisiogest.pacientes.domain.paciente import DatosPaciente
from fisiogest.pacientes.features.actualizar_paciente.caso_uso import ActualizarPaciente
from fisiogest.shared.domain.errors import (
    ConflictError,
    DomainError,
    NotFoundError,
    ValidationError,
)
from fisiogest.shared.web.http import contenedor, formulario, requiere_rol
from fisiogest.usuarios.domain.usuario import Rol

bp = Blueprint(
    "actualizar_paciente", __name__, template_folder="templates", url_prefix="/pacientes"
)

ROLES = (Rol.ADMINISTRADOR, Rol.RECEPCIONISTA)
CAMPOS = [f.name for f in fields(DatosPaciente)]


def _caso_uso() -> ActualizarPaciente:
    return ActualizarPaciente(contenedor().pacientes)


@bp.get("/<int:paciente_id>/editar")
@requiere_rol(*ROLES)
def formulario_edicion(paciente_id: int):
    try:
        paciente = _caso_uso().obtener(paciente_id)
    except NotFoundError:
        abort(404)
    datos = {campo: getattr(paciente, campo) or "" for campo in CAMPOS}
    return render_template("pacientes/actualizar.html", paciente=paciente, datos=datos, errores={})


@bp.post("/<int:paciente_id>/editar")
@requiere_rol(*ROLES)
def actualizar(paciente_id: int):
    caso_uso = _caso_uso()
    datos = formulario()
    try:
        paciente = caso_uso.ejecutar(
            paciente_id, DatosPaciente(**{k: v for k, v in datos.items() if k in CAMPOS})
        )
    except NotFoundError:
        abort(404)
    except ValidationError as error:
        paciente = caso_uso.obtener(paciente_id)
        return (
            render_template(
                "pacientes/actualizar.html", paciente=paciente, datos=datos, errores=error.errores
            ),
            422,
        )
    except ConflictError as error:
        paciente = caso_uso.obtener(paciente_id)
        errores = {"cedula": str(error)}
        return (
            render_template(
                "pacientes/actualizar.html", paciente=paciente, datos=datos, errores=errores
            ),
            409,
        )
    except DomainError as error:
        flash(str(error), "error")
        return redirect(url_for("consultar_historial.ver", paciente_id=paciente_id))
    flash("Datos del paciente actualizados.", "exito")
    return redirect(url_for("consultar_historial.ver", paciente_id=paciente.id))
