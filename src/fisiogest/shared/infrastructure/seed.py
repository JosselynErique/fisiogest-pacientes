"""Datos iniciales.

- Siempre: si no hay usuarios, crea las cuentas base.
- Modo demo (FISIOGEST_DEMO=1): además crea pacientes, citas y sesiones ficticias
  (cédulas sintéticas válidas) para poder recorrer el sistema recién clonado.
"""

from __future__ import annotations

import os
import random
import secrets
from datetime import date, datetime, time, timedelta
from typing import TYPE_CHECKING

from fisiogest.citas.domain.cita import Cita, EstadoCita
from fisiogest.pacientes.domain.paciente import Paciente
from fisiogest.terapias.domain.terapia import TIPOS_TERAPIA, Terapia
from fisiogest.usuarios.domain.usuario import Rol, Usuario

if TYPE_CHECKING:
    from fisiogest.container import Container

PASSWORD_DEMO = "Fisio2026"

USUARIOS_DEMO = (
    ("admin", "Administrador del Consultorio", Rol.ADMINISTRADOR),
    ("recepcion", "María Fernanda López", Rol.RECEPCIONISTA),
    ("fisio.ana", "Ana Lucía Cárdenas", Rol.FISIOTERAPEUTA),
    ("fisio.carlos", "Carlos Andrés Villacís", Rol.FISIOTERAPEUTA),
)

PACIENTES_DEMO = (
    ("1722601810", "Daniela", "Andrade Mora", "1990-04-12", "0991234567", "Quito, La Floresta"),
    ("1129083018", "Jorge Luis", "Benítez Salazar", "1978-09-30", "0987654321", "Loja, Centro"),
    ("1636131862", "Paola", "Cevallos Rivera", "1985-01-22", "0998877665", "Puyo, Barrio México"),
    ("0909139099", "Ricardo", "Delgado Vera", "1969-11-05", "0976543210", "Guayaquil, Urdesa"),
    ("0146030820", "Gabriela", "Espinoza Torres", "2001-06-18", "0961122334", "Cuenca, El Vergel"),
    ("1826281949", "Miguel Ángel", "Fuentes Ortiz", "1995-03-02", "0955566778", "Ambato, Ficoa"),
    ("0742199359", "Lucía", "Guerrero Páez", "1958-08-14", "0944433221", "Machala, La Providencia"),
    ("1508190939", "Santiago", "Herrera Núñez", "2008-12-01", "0933344556", "Tena, Centro"),
    ("2238657973", "Valeria", "Iturralde Cruz", "1999-07-27", "0922211003", "Lago Agrio, Central"),
    (
        "0524323193",
        "Fernando",
        "Jaramillo León",
        "1982-02-09",
        "0911100998",
        "Latacunga, San Felipe",
    ),
)

MOTIVOS = (
    "Dolor lumbar crónico",
    "Rehabilitación de rodilla postquirúrgica",
    "Esguince de tobillo grado II",
    "Cervicalgia por postura",
    "Tendinitis del manguito rotador",
    "Fascitis plantar",
)

ZONAS = (
    "Zona lumbar",
    "Rodilla derecha",
    "Tobillo izquierdo",
    "Cervical",
    "Hombro derecho",
    "Pie izquierdo",
)


def cargar_datos_iniciales(c: Container, demo: bool) -> None:
    if c.usuarios.contar() == 0:
        if demo:
            for username, nombre, rol in USUARIOS_DEMO:
                c.usuarios.guardar(Usuario(username, nombre, rol, c.hasher.hashear(PASSWORD_DEMO)))
        else:
            password = os.environ.get("FISIOGEST_ADMIN_PASSWORD") or secrets.token_urlsafe(12)
            c.usuarios.guardar(
                Usuario("admin", "Administrador", Rol.ADMINISTRADOR, c.hasher.hashear(password))
            )
            if "FISIOGEST_ADMIN_PASSWORD" not in os.environ:
                print(f"[FisioGest] Usuario 'admin' creado. Contraseña temporal: {password}")

    if demo and c.pacientes.contar(solo_activos=False) == 0:
        _cargar_demo_clinica(c)


def _cargar_demo_clinica(c: Container) -> None:
    azar = random.Random(2026)
    ahora = c.reloj()
    hoy = ahora.date()
    fisios = c.usuarios.listar(Rol.FISIOTERAPEUTA)

    pacientes = []
    for i, (cedula, nombres, apellidos, nacimiento, telefono, direccion) in enumerate(
        PACIENTES_DEMO
    ):
        pacientes.append(
            c.pacientes.guardar(
                Paciente(
                    cedula=cedula,
                    nombres=nombres,
                    apellidos=apellidos,
                    fecha_nacimiento=date.fromisoformat(nacimiento),
                    telefono=telefono,
                    correo=f"{nombres.split()[0].lower()}.{apellidos.split()[0].lower()}@correo.ec".replace(
                        "á", "a"
                    )
                    .replace("é", "e")
                    .replace("í", "i")
                    .replace("ó", "o")
                    .replace("ú", "u"),
                    direccion=direccion,
                    contacto_emergencia="Familiar · 0990000000",
                    creado_en=datetime.combine(hoy - timedelta(days=40 - i * 3), time(9, 0)),
                )
            )
        )

    ocupados: set[tuple[int, date, time]] = set()

    def crear_cita(
        paciente: Paciente, fisio: Usuario, dia: date, hora: time, motivo: str
    ) -> Cita | None:
        if dia.weekday() == 6 or (fisio.id, dia, hora) in ocupados:
            return None
        ocupados.add((fisio.id, dia, hora))
        inicio = datetime.combine(dia, hora)
        return Cita(
            paciente_id=paciente.id,
            fisioterapeuta_id=fisio.id,
            fecha=dia,
            hora_inicio=hora,
            hora_fin=(inicio + timedelta(minutes=45)).time(),
            motivo=motivo,
            creado_en=inicio - timedelta(days=3),
        )

    horas = [time(h, 0) for h in range(8, 18)]

    def registrar_sesion(paciente, fisio, cita, zona, dolor) -> int:
        cita.estado = EstadoCita.ATENDIDA
        c.citas.guardar(cita)
        final = max(0, dolor - azar.randint(1, 3))
        c.terapias.guardar(
            Terapia(
                paciente_id=paciente.id,
                fisioterapeuta_id=fisio.id,
                cita_id=cita.id,
                fecha=cita.fecha,
                tipo=azar.choice(TIPOS_TERAPIA[:8]),
                zona_tratada=zona,
                dolor_inicial=dolor,
                dolor_final=final,
                procedimiento="Movilización articular, ejercicios de fortalecimiento y estiramiento guiado.",
                observaciones=azar.choice(
                    ("Buena tolerancia al tratamiento.", "Indicar ejercicios en casa.", "")
                ),
            )
        )
        return max(1, final + azar.randint(0, 1))

    for indice, paciente in enumerate(pacientes):
        fisio = fisios[indice % len(fisios)]
        motivo = MOTIVOS[indice % len(MOTIVOS)]
        zona = ZONAS[indice % len(ZONAS)]
        dolor = azar.randint(6, 9)
        # Sesiones pasadas: unas dos por semana durante el último mes (incluye los últimos días)
        for dias_atras in (27, 24, 20, 17, 13, 10, 6, 3, 1):
            dia = hoy - timedelta(days=dias_atras + indice % 2)
            cita = crear_cita(paciente, fisio, dia, azar.choice(horas), motivo)
            if cita is None:
                continue
            if azar.random() < 0.12:
                cita.estado = EstadoCita.CANCELADA
                cita.motivo_cancelacion = "El paciente avisó que no podía asistir"
                c.citas.guardar(cita)
                continue
            dolor = registrar_sesion(paciente, fisio, cita, zona, dolor)
        # Agenda de hoy: las citas que ya pasaron quedan atendidas, el resto programadas
        cita = crear_cita(paciente, fisio, hoy, time(8 + indice, 0), motivo)
        if cita is not None:
            if datetime.combine(hoy, cita.hora_inicio) < ahora:
                dolor = registrar_sesion(paciente, fisio, cita, zona, dolor)
            else:
                c.citas.guardar(cita)
        # Próximas citas
        for dias in (2, 7):
            cita = crear_cita(
                paciente, fisio, hoy + timedelta(days=dias), azar.choice(horas), motivo
            )
            if cita is not None:
                c.citas.guardar(cita)
