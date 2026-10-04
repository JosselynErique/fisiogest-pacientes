"""Adaptadores SQLite contra una base de datos real (archivo temporal)."""

import sqlite3
from datetime import date, time

import pytest

from fisiogest.citas.domain.cita import Cita, EstadoCita
from fisiogest.pacientes.domain.paciente import DatosPaciente, Paciente
from fisiogest.reportes.domain.reporte import Periodo
from fisiogest.shared.infrastructure.database import Database
from fisiogest.terapias.domain.terapia import Terapia
from fisiogest.usuarios.domain.usuario import Rol
from helpers import CEDULA_1, CEDULA_2, CEDULA_3

pytestmark = pytest.mark.integration


def test_database_es_singleton_por_archivo(contenedor):
    assert Database(contenedor.db.ruta) is contenedor.db


def test_paciente_ida_y_vuelta(contenedor):
    repo = contenedor.pacientes
    guardado = repo.guardar(
        Paciente.crear(
            DatosPaciente(CEDULA_1, "Ana", "Mora", "1990-05-01", "0991234567", "ana@correo.ec")
        )
    )
    leido = repo.obtener(guardado.id)
    assert leido == guardado
    assert repo.obtener_por_cedula(CEDULA_1).id == guardado.id


def test_busqueda_por_nombre_cedula_y_estado(contenedor):
    repo = contenedor.pacientes
    for cedula, nombres, apellidos in (
        (CEDULA_1, "Ana", "Mora"),
        (CEDULA_2, "Jorge", "Vera"),
        (CEDULA_3, "Paola", "Mora"),
    ):
        repo.guardar(Paciente.crear(DatosPaciente(cedula, nombres, apellidos)))
    assert {p.nombres for p in repo.buscar("mora")} == {"Ana", "Paola"}
    assert [p.nombres for p in repo.buscar(CEDULA_2[:5])] == ["Jorge"]
    jorge = repo.buscar("jorge")[0]
    jorge.dar_de_baja()
    repo.guardar(jorge)
    assert repo.buscar("jorge") == []
    assert repo.contar() == 2 and repo.contar(solo_activos=False) == 3


def test_la_base_impide_cedulas_duplicadas(contenedor):
    repo = contenedor.pacientes
    repo.guardar(Paciente.crear(DatosPaciente(CEDULA_1, "Ana", "Mora")))
    with pytest.raises(sqlite3.IntegrityError):
        repo.guardar(Paciente.crear(DatosPaciente(CEDULA_1, "Otra", "Persona")))


def test_citas_agenda_y_reporte(contenedor):
    paciente = contenedor.pacientes.guardar(Paciente.crear(DatosPaciente(CEDULA_1, "Ana", "Mora")))
    fisio = contenedor.usuarios.listar(Rol.FISIOTERAPEUTA)[0]
    dia = date(2026, 10, 6)
    atendida = contenedor.citas.guardar(
        Cita(paciente.id, fisio.id, dia, time(9), time(9, 45), "Dolor", EstadoCita.ATENDIDA)
    )
    contenedor.citas.guardar(
        Cita(paciente.id, fisio.id, dia, time(11), time(11, 45), "Control", EstadoCita.CANCELADA)
    )
    contenedor.terapias.guardar(
        Terapia(
            paciente.id,
            fisio.id,
            dia,
            "Terapia manual",
            "Cervical",
            8,
            5,
            "Masaje",
            cita_id=atendida.id,
        )
    )

    agenda = contenedor.citas.agenda(dia, dia, fisioterapeuta_id=fisio.id)
    assert [d.cita.hora_inicio for d in agenda] == [time(9), time(11)]
    assert agenda[0].paciente_nombre == "Ana Mora"
    assert len(contenedor.citas.activas_del_fisioterapeuta(fisio.id, dia)) == 1

    reporte = contenedor.reportes.generar(Periodo(dia, dia))
    assert reporte.sesiones == 1
    assert reporte.pacientes_atendidos == 1
    assert reporte.citas_por_estado == {"programada": 0, "atendida": 1, "cancelada": 1}
    assert reporte.tasa_cancelacion == 50.0
    assert reporte.mejora_promedio == 3.0
    assert reporte.terapias_por_tipo == [("Terapia manual", 1)]


def test_una_cita_solo_puede_tener_una_sesion(contenedor):
    paciente = contenedor.pacientes.guardar(Paciente.crear(DatosPaciente(CEDULA_1, "Ana", "Mora")))
    fisio = contenedor.usuarios.listar(Rol.FISIOTERAPEUTA)[0]
    dia = date(2026, 10, 5)
    cita = contenedor.citas.guardar(Cita(paciente.id, fisio.id, dia, time(9), time(9, 45)))
    sesion = Terapia(
        paciente.id, fisio.id, dia, "Otro", "Hombro", 5, 3, "Ejercicio", cita_id=cita.id
    )
    contenedor.terapias.guardar(sesion)
    sesion.id = None
    with pytest.raises(sqlite3.IntegrityError):
        contenedor.terapias.guardar(sesion)
