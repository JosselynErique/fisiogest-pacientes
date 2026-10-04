"""CP-06 (aceptación): flujo completo de un día en el consultorio, desde la perspectiva
de cada rol, usando únicamente la interfaz web.
"""

from datetime import date

import pytest

from helpers import CEDULA_1

pytestmark = pytest.mark.acceptance
DIA = date(2026, 10, 5)


def test_cp06_flujo_completo_del_consultorio(como, contenedor):
    # 1. La recepcionista registra al paciente (RF-01) y le agenda una cita (RF-04).
    recepcion = como("recepcion")
    r = recepcion.post(
        "/pacientes/nuevo",
        data={
            "cedula": CEDULA_1,
            "nombres": "Daniela",
            "apellidos": "Andrade",
            "fecha_nacimiento": "1990-04-12",
            "telefono": "0991234567",
            "_csrf": recepcion.csrf,
        },
        follow_redirects=True,
    )
    assert b"Daniela Andrade registrado correctamente" in r.data
    paciente = contenedor.pacientes.obtener_por_cedula(CEDULA_1)
    ana = contenedor.usuarios.obtener_por_username("fisio.ana")

    r = recepcion.post(
        "/citas/nueva",
        data={
            "paciente_id": paciente.id,
            "fisioterapeuta_id": ana.id,
            "fecha": "2026-10-05",
            "hora_inicio": "09:00",
            "duracion_minutos": "45",
            "motivo": "Dolor lumbar",
            "_csrf": recepcion.csrf,
        },
        follow_redirects=True,
    )
    assert b"Cita agendada" in r.data

    # 2. La fisioterapeuta ve la cita en su agenda y registra la sesión (RF-06).
    fisio = como("fisio.ana")
    agenda = fisio.get("/citas/?fecha=2026-10-05")
    assert b"Daniela Andrade" in agenda.data
    cita = contenedor.citas.agenda(paciente_id=paciente.id, desde=DIA, hasta=DIA)[0].cita

    r = fisio.post(
        f"/citas/{cita.id}/atender",
        data={
            "fecha": "2026-10-05",
            "tipo": "Terapia manual",
            "zona_tratada": "Zona lumbar",
            "dolor_inicial": "8",
            "dolor_final": "5",
            "procedimiento": "Movilización lumbar y ejercicios de core",
            "observaciones": "Continuar ejercicios en casa",
            "_csrf": fisio.csrf,
        },
        follow_redirects=True,
    )
    assert "La cita quedó como atendida".encode() in r.data

    # 3. El historial clínico refleja la sesión y la evolución del dolor (RF-07).
    historial = fisio.get(f"/pacientes/{paciente.id}")
    assert "Movilización lumbar".encode() in historial.data
    assert "8 → 5".encode() in historial.data

    # 4. El administrador obtiene el reporte del periodo y lo exporta (RF-08).
    admin = como("admin")
    reporte = admin.get("/reportes/?desde=2026-10-01&hasta=2026-10-31")
    assert reporte.status_code == 200
    assert b"Pacientes atendidos" in reporte.data
    csv = admin.get("/reportes/exportar.csv?desde=2026-10-01&hasta=2026-10-31")
    assert csv.mimetype == "text/csv"
    assert "Sesiones de terapia;1" in csv.get_data(as_text=True)
