"""Raíz de composición: conecta cada puerto con su adaptador concreto.

Es el único lugar que conoce las implementaciones (SQLite, werkzeug). Cambiar la base
de datos implicaría escribir nuevos adaptadores y modificar solo este archivo.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from fisiogest.citas.adapters.sqlite_cita_repository import SqliteCitaRepository
from fisiogest.citas.domain.ports import CitaRepository
from fisiogest.config import Config
from fisiogest.pacientes.adapters.sqlite_paciente_repository import SqlitePacienteRepository
from fisiogest.pacientes.domain.ports import PacienteRepository
from fisiogest.reportes.adapters.sqlite_reporte_query import SqliteReporteQuery
from fisiogest.reportes.domain.ports import ReporteQuery
from fisiogest.shared.infrastructure.database import Database
from fisiogest.terapias.adapters.sqlite_terapia_repository import SqliteTerapiaRepository
from fisiogest.terapias.domain.ports import TerapiaRepository
from fisiogest.usuarios.adapters.sqlite_usuario_repository import SqliteUsuarioRepository
from fisiogest.usuarios.adapters.werkzeug_password_hasher import WerkzeugPasswordHasher
from fisiogest.usuarios.domain.ports import PasswordHasher, UsuarioRepository


@dataclass
class Container:
    db: Database
    usuarios: UsuarioRepository
    hasher: PasswordHasher
    pacientes: PacienteRepository
    citas: CitaRepository
    terapias: TerapiaRepository
    reportes: ReporteQuery
    reloj: Callable[[], datetime] = datetime.now


def construir_contenedor(config: Config, reloj: Callable[[], datetime] = datetime.now) -> Container:
    db = Database(config.database)
    return Container(
        db=db,
        usuarios=SqliteUsuarioRepository(db),
        hasher=WerkzeugPasswordHasher(),
        pacientes=SqlitePacienteRepository(db),
        citas=SqliteCitaRepository(db),
        terapias=SqliteTerapiaRepository(db),
        reportes=SqliteReporteQuery(db),
        reloj=reloj,
    )
