"""Puertos (interfaces) del módulo de usuarios. Los adaptadores los implementan."""

from __future__ import annotations

from typing import Protocol

from fisiogest.usuarios.domain.usuario import Rol, Usuario


class UsuarioRepository(Protocol):
    def guardar(self, usuario: Usuario) -> Usuario: ...

    def obtener(self, usuario_id: int) -> Usuario | None: ...

    def obtener_por_username(self, username: str) -> Usuario | None: ...

    def listar(self, rol: Rol | None = None, solo_activos: bool = False) -> list[Usuario]: ...

    def contar(self) -> int: ...


class PasswordHasher(Protocol):
    def hashear(self, password: str) -> str: ...

    def verificar(self, password_hash: str, password: str) -> bool: ...
