"""Adaptador de salida: implementa UsuarioRepository sobre SQLite (patrón DAO)."""

from __future__ import annotations

import sqlite3
from datetime import datetime

from fisiogest.shared.infrastructure.database import Database
from fisiogest.usuarios.domain.usuario import Rol, Usuario


def _a_usuario(fila: sqlite3.Row) -> Usuario:
    return Usuario(
        id=fila["id"],
        username=fila["username"],
        nombre_completo=fila["nombre_completo"],
        rol=Rol(fila["rol"]),
        password_hash=fila["password_hash"],
        activo=bool(fila["activo"]),
        intentos_fallidos=fila["intentos_fallidos"],
        bloqueado_hasta=(
            datetime.fromisoformat(fila["bloqueado_hasta"]) if fila["bloqueado_hasta"] else None
        ),
        creado_en=datetime.fromisoformat(fila["creado_en"]),
    )


class SqliteUsuarioRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    def guardar(self, usuario: Usuario) -> Usuario:
        valores = (
            usuario.username,
            usuario.nombre_completo,
            usuario.rol.value,
            usuario.password_hash,
            int(usuario.activo),
            usuario.intentos_fallidos,
            usuario.bloqueado_hasta.isoformat() if usuario.bloqueado_hasta else None,
        )
        with self._db.conexion() as con:
            if usuario.id is None:
                cursor = con.execute(
                    """INSERT INTO usuarios (username, nombre_completo, rol, password_hash, activo,
                           intentos_fallidos, bloqueado_hasta, creado_en)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (*valores, usuario.creado_en.isoformat(timespec="seconds")),
                )
                usuario.id = cursor.lastrowid
            else:
                con.execute(
                    """UPDATE usuarios SET username = ?, nombre_completo = ?, rol = ?,
                           password_hash = ?, activo = ?, intentos_fallidos = ?, bloqueado_hasta = ?
                       WHERE id = ?""",
                    (*valores, usuario.id),
                )
        return usuario

    def obtener(self, usuario_id: int) -> Usuario | None:
        with self._db.conexion() as con:
            fila = con.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
        return _a_usuario(fila) if fila else None

    def obtener_por_username(self, username: str) -> Usuario | None:
        with self._db.conexion() as con:
            fila = con.execute(
                "SELECT * FROM usuarios WHERE username = ?", (username.lower(),)
            ).fetchone()
        return _a_usuario(fila) if fila else None

    def listar(self, rol: Rol | None = None, solo_activos: bool = False) -> list[Usuario]:
        sql = "SELECT * FROM usuarios WHERE 1 = 1"
        params: list[object] = []
        if rol is not None:
            sql += " AND rol = ?"
            params.append(rol.value)
        if solo_activos:
            sql += " AND activo = 1"
        sql += " ORDER BY nombre_completo"
        with self._db.conexion() as con:
            return [_a_usuario(f) for f in con.execute(sql, params).fetchall()]

    def contar(self) -> int:
        with self._db.conexion() as con:
            return con.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
