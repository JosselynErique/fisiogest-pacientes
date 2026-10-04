from dataclasses import fields

from flask import Blueprint, abort, flash, redirect, render_template, url_for

from fisiogest.shared.domain.errors import DomainError, NotFoundError, ValidationError
from fisiogest.shared.web.http import contenedor, formulario, requiere_rol, usuario_actual
from fisiogest.terapias.domain.terapia import TIPOS_TERAPIA, DatosTerapia
from fisiogest.terapias.features.registrar_terapia.caso_uso import RegistrarTerapia
from fisiogest.usuarios.domain.usuario import Rol

bp = Blueprint("registrar_terapia", __name__, template_folder="templates")

ROLES = (Rol.FISIOTERAPEUTA, Rol.ADMINISTRADOR)
CAMPOS = [f.name for f in fields(DatosTerapia)]
TIPOS = [(t, t) for t in TIPOS_TERAPIA]
EVA = [(n, f"{n}") for n in range(11)]


def _caso_uso() -> RegistrarTerapia:
    c = contenedor()
    return RegistrarTerapia(c.terapias, c.pacientes, c.citas, c.reloj)


def _render(paciente, datos, errores, cita=None, estado=200):
    html = render_template(
        "terapias/registrar.html",
        paciente=paciente,
        cita=cita,
        datos=datos,
        errores=errores,
        tipos=TIPOS,
        eva=EVA,
    )
    return html, estado


def _datos() -> tuple[dict, DatosTerapia]:
    datos = formulario()
    return datos, DatosTerapia(**{k: v for k, v in datos.items() if k in CAMPOS})


@bp.get("/citas/<int:cita_id>/atender")
@requiere_rol(*ROLES)
def formulario_cita(cita_id: int):
    caso_uso = _caso_uso()
    try:
        cita = caso_uso.cita_para_atender(cita_id, usuario_actual())
    except NotFoundError:
        abort(404)
    except DomainError as error:
        flash(str(error), "error")
        return redirect(url_for("consultar_agenda.ver"))
    paciente = caso_uso.paciente(cita.paciente_id)
    return _render(paciente, {"fecha": cita.fecha.isoformat()}, {}, cita)


@bp.post("/citas/<int:cita_id>/atender")
@requiere_rol(*ROLES)
def registrar_desde_cita(cita_id: int):
    caso_uso = _caso_uso()
    datos, comando = _datos()
    try:
        terapia = caso_uso.desde_cita(cita_id, comando, usuario_actual())
    except NotFoundError:
        abort(404)
    except ValidationError as error:
        cita = caso_uso.cita_para_atender(cita_id, usuario_actual())
        return _render(caso_uso.paciente(cita.paciente_id), datos, error.errores, cita, 422)
    except DomainError as error:
        flash(str(error), "error")
        return redirect(url_for("consultar_agenda.ver"))
    flash("Sesión registrada. La cita quedó como atendida.", "exito")
    return redirect(url_for("consultar_historial.ver", paciente_id=terapia.paciente_id))


@bp.get("/pacientes/<int:paciente_id>/terapias/nueva")
@requiere_rol(Rol.FISIOTERAPEUTA)
def formulario_paciente(paciente_id: int):
    caso_uso = _caso_uso()
    try:
        paciente = caso_uso.paciente(paciente_id)
    except NotFoundError:
        abort(404)
    return _render(paciente, {"fecha": contenedor().reloj().date().isoformat()}, {})


@bp.post("/pacientes/<int:paciente_id>/terapias/nueva")
@requiere_rol(Rol.FISIOTERAPEUTA)
def registrar_para_paciente(paciente_id: int):
    caso_uso = _caso_uso()
    datos, comando = _datos()
    try:
        caso_uso.sin_cita(paciente_id, comando, usuario_actual())
    except NotFoundError:
        abort(404)
    except ValidationError as error:
        return _render(caso_uso.paciente(paciente_id), datos, error.errores, estado=422)
    except DomainError as error:
        flash(str(error), "error")
        return redirect(url_for("consultar_historial.ver", paciente_id=paciente_id))
    flash("Sesión de terapia registrada.", "exito")
    return redirect(url_for("consultar_historial.ver", paciente_id=paciente_id))
