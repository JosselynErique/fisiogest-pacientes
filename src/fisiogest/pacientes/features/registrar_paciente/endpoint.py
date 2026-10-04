from flask import Blueprint, flash, redirect, render_template, url_for

from fisiogest.pacientes.domain.paciente import DatosPaciente
from fisiogest.pacientes.features.registrar_paciente.caso_uso import RegistrarPaciente
from fisiogest.shared.domain.errors import ConflictError, ValidationError
from fisiogest.shared.web.http import contenedor, formulario, requiere_rol
from fisiogest.usuarios.domain.usuario import Rol

bp = Blueprint("registrar_paciente", __name__, template_folder="templates", url_prefix="/pacientes")

ROLES = (Rol.ADMINISTRADOR, Rol.RECEPCIONISTA)


@bp.get("/nuevo")
@requiere_rol(*ROLES)
def formulario_nuevo():
    return render_template("pacientes/registrar.html", datos={}, errores={})


@bp.post("/nuevo")
@requiere_rol(*ROLES)
def registrar():
    datos = formulario()
    try:
        paciente = RegistrarPaciente(contenedor().pacientes).ejecutar(
            DatosPaciente(
                **{k: v for k, v in datos.items() if k in DatosPaciente.__dataclass_fields__}
            )
        )
    except ValidationError as error:
        return render_template("pacientes/registrar.html", datos=datos, errores=error.errores), 422
    except ConflictError as error:
        return render_template(
            "pacientes/registrar.html", datos=datos, errores={"cedula": str(error)}
        ), 409
    flash(f"Paciente {paciente.nombre_completo} registrado correctamente.", "exito")
    return redirect(url_for("consultar_historial.ver", paciente_id=paciente.id))
