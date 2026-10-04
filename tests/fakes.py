"""Adaptadores en memoria para probar los casos de uso sin base de datos ni HTTP.

Que estos dobles puedan sustituir a SQLite demuestra el desacople de la arquitectura
hexagonal: los casos de uso solo dependen de los puertos.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date

from fisiogest.citas.domain.cita import Cita, CitaDetalle, EstadoCita
from fisiogest.pacientes.domain.paciente import Paciente
from fisiogest.terapias.domain.terapia import Terapia, TerapiaDetalle
from fisiogest.usuarios.domain.usuario import Rol, Usuario


class _Memoria:
    def __init__(self) -> None:
        self.datos: dict[int, object] = {}
        self._siguiente = 1

    def _guardar(self, entidad):
        if entidad.id is None:
            entidad.id = self._siguiente
            self._siguiente += 1
        self.datos[entidad.id] = replace(entidad)
        return entidad

    def _obtener(self, entidad_id):
        entidad = self.datos.get(entidad_id)
        return replace(entidad) if entidad else None


class PacientesEnMemoria(_Memoria):
    def guardar(self, paciente: Paciente) -> Paciente:
        return self._guardar(paciente)

    def obtener(self, paciente_id: int) -> Paciente | None:
        return self._obtener(paciente_id)

    def obtener_por_cedula(self, cedula: str) -> Paciente | None:
        return next((replace(p) for p in self.datos.values() if p.cedula == cedula), None)

    def buscar(self, texto: str = "", incluir_inactivos: bool = False) -> list[Paciente]:
        texto = texto.lower()
        return [
            replace(p)
            for p in self.datos.values()
            if (incluir_inactivos or p.activo)
            and (texto in p.cedula or texto in p.nombre_completo.lower())
        ]

    def contar(self, solo_activos: bool = True) -> int:
        return sum(1 for p in self.datos.values() if p.activo or not solo_activos)


class UsuariosEnMemoria(_Memoria):
    def guardar(self, usuario: Usuario) -> Usuario:
        return self._guardar(usuario)

    def obtener(self, usuario_id: int) -> Usuario | None:
        return self._obtener(usuario_id)

    def obtener_por_username(self, username: str) -> Usuario | None:
        return next((replace(u) for u in self.datos.values() if u.username == username), None)

    def listar(self, rol: Rol | None = None, solo_activos: bool = False) -> list[Usuario]:
        return [
            replace(u)
            for u in self.datos.values()
            if (rol is None or u.rol is rol) and (u.activo or not solo_activos)
        ]

    def contar(self) -> int:
        return len(self.datos)


class CitasEnMemoria(_Memoria):
    def guardar(self, cita: Cita) -> Cita:
        return self._guardar(cita)

    def obtener(self, cita_id: int) -> Cita | None:
        return self._obtener(cita_id)

    def obtener_detalle(self, cita_id: int) -> CitaDetalle | None:
        cita = self._obtener(cita_id)
        return CitaDetalle(cita, "Paciente", "0000000000", "Fisio") if cita else None

    def _activas(self, filtro) -> list[Cita]:
        return [
            replace(c)
            for c in self.datos.values()
            if filtro(c) and c.estado is not EstadoCita.CANCELADA
        ]

    def activas_del_fisioterapeuta(self, fisioterapeuta_id: int, fecha: date) -> list[Cita]:
        return self._activas(
            lambda c: c.fisioterapeuta_id == fisioterapeuta_id and c.fecha == fecha
        )

    def activas_del_paciente(self, paciente_id: int, fecha: date) -> list[Cita]:
        return self._activas(lambda c: c.paciente_id == paciente_id and c.fecha == fecha)

    def agenda(self, desde, hasta, fisioterapeuta_id=None, paciente_id=None) -> list[CitaDetalle]:
        return [
            CitaDetalle(replace(c), "Paciente", "0000000000", "Fisio")
            for c in self.datos.values()
            if desde <= c.fecha <= hasta
            and (fisioterapeuta_id is None or c.fisioterapeuta_id == fisioterapeuta_id)
            and (paciente_id is None or c.paciente_id == paciente_id)
        ]


class TerapiasEnMemoria(_Memoria):
    def guardar(self, terapia: Terapia) -> Terapia:
        return self._guardar(terapia)

    def del_paciente(self, paciente_id: int) -> list[TerapiaDetalle]:
        return [
            TerapiaDetalle(replace(t), "Fisio")
            for t in sorted(self.datos.values(), key=lambda t: t.fecha, reverse=True)
            if t.paciente_id == paciente_id
        ]


class HasherFalso:
    """Hasher trivial y determinista: suficiente para probar la lógica de autenticación."""

    def hashear(self, password: str) -> str:
        return f"hash::{password}"

    def verificar(self, password_hash: str, password: str) -> bool:
        return password_hash == f"hash::{password}"
