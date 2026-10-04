"""Exporta el reporte del periodo a CSV (abre directamente en Excel)."""

import csv
import io

from flask import Blueprint, Response, abort, request

from fisiogest.reportes.domain.reporte import Reporte
from fisiogest.reportes.features.generar_reporte.caso_uso import GenerarReporte
from fisiogest.shared.domain.errors import ValidationError
from fisiogest.shared.domain.validators import parsear_fecha
from fisiogest.shared.web.http import contenedor, requiere_rol
from fisiogest.usuarios.domain.usuario import Rol

bp = Blueprint("exportar_reporte", __name__, url_prefix="/reportes")


def a_csv(reporte: Reporte) -> str:
    salida = io.StringIO()
    w = csv.writer(salida, delimiter=";")
    w.writerow(
        [
            "Reporte FisioGest",
            f"{reporte.periodo.desde:%d/%m/%Y}",
            f"{reporte.periodo.hasta:%d/%m/%Y}",
        ]
    )
    w.writerow([])
    w.writerow(["Indicador", "Valor"])
    w.writerow(["Pacientes atendidos", reporte.pacientes_atendidos])
    w.writerow(["Pacientes nuevos", reporte.pacientes_nuevos])
    w.writerow(["Sesiones de terapia", reporte.sesiones])
    for estado, total in reporte.citas_por_estado.items():
        w.writerow([f"Citas {estado}s", total])
    w.writerow(["Tasa de cancelación (%)", reporte.tasa_cancelacion])
    w.writerow(["Mejora promedio de dolor (EVA)", reporte.mejora_promedio or ""])
    w.writerow([])
    w.writerow(["Fisioterapeuta", "Citas atendidas", "Sesiones", "Pacientes", "Mejora prom. EVA"])
    for f in reporte.por_fisioterapeuta:
        w.writerow([f.nombre, f.citas_atendidas, f.sesiones, f.pacientes, f.mejora_promedio or ""])
    w.writerow([])
    w.writerow(["Tipo de terapia", "Sesiones"])
    for tipo, total in reporte.terapias_por_tipo:
        w.writerow([tipo, total])
    return salida.getvalue()


@bp.get("/exportar.csv", endpoint="csv")
@requiere_rol(Rol.ADMINISTRADOR)
def csv_():
    try:
        reporte = GenerarReporte(contenedor().reportes).ejecutar(
            parsear_fecha(request.args.get("desde", "")),
            parsear_fecha(request.args.get("hasta", "")),
        )
    except ValidationError as error:
        abort(400, description=str(error))
    nombre = f"reporte_fisiogest_{reporte.periodo.desde}_{reporte.periodo.hasta}.csv"
    return Response(
        "﻿" + a_csv(reporte),
        mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{nombre}"'},
    )
