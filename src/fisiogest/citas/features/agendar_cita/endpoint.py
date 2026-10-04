from dataclasses import fields

from flask import Blueprint, flash, redirect, render_template, request, url_for

from fisiogest.citas.domain.cita import DURACIONES_MINUTOS, DatosCita
from fisiogest.citas.features.agendar_cita.caso_uso import AgendarCita
from fisiogest.shared.domain.errors import ConflictError, ValidationError
from fisiogest.shared.web.http import contenedor, formulario, requiere_rol
from fisiogest.usuarios.domain.usuario import Rol

bp = Blueprint("agendar_cita", __name__, template_folder="templates", url_prefix="/citas")

ROLES = (Rol.ADMINISTRADOR, Rol.RECEPCIONISTA)
CAMPOS = [f.name for f in fields(DatosCita)]


def _render(datos: dict, errores: dict, estado: int = 200):
    c = contenedor()
    pacientes = [(p.id, f"{p.apellidos} {p.nombres} · {p.cedula}") for p in c.pacientes.buscar()]
    fisios = [
        (u.id, u.nombre_completo) for u in c.usuarios.listar(Rol.FISIOTERAPEUTA, solo_activos=True)
    ]
    duraciones = [(d, f"{d} minutos") for d in DURACIONES_MINUTOS]
    html = render_template(
        "citas/agendar.html",
        datos=datos,
        errores=errores,
        pacientes=pacientes,
        fisios=fisios,
        duraciones=duraciones,
    )
    return html, estado


@bp.get("/nueva")
@requiere_rol(*ROLES)
def formulario_nuevo():
    datos = {
        "paciente_id": request.args.get("paciente_id", ""),
        "fecha": request.args.get("fecha", ""),
        "duracion_minutos": "45",
    }
    return _render(datos, {})


@bp.post("/nueva")
@requiere_rol(*ROLES)
def agendar():
    datos = formulario()
    c = contenedor()
    try:
        cita = AgendarCita(c.citas, c.pacientes, c.usuarios, c.reloj).ejecutar(
            DatosCita(**{k: v for k, v in datos.items() if k in CAMPOS})
        )
    except ValidationError as error:
        return _render(datos, error.errores, 422)
    except ConflictError as error:
        return _render(datos, {"hora_inicio": str(error)}, 409)
    flash(
        f"Cita agendada para el {cita.fecha:%d/%m/%Y} de {cita.hora_inicio:%H:%M} a {cita.hora_fin:%H:%M}.",
        "exito",
    )
    return redirect(url_for("consultar_agenda.ver", fecha=cita.fecha.isoformat()))
