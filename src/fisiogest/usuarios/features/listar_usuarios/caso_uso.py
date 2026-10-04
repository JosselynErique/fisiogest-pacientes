from __future__ import annotations

from fisiogest.usuarios.domain.ports import UsuarioRepository
from fisiogest.usuarios.domain.usuario import Usuario


class ListarUsuarios:
    def __init__(self, usuarios: UsuarioRepository) -> None:
        self._usuarios = usuarios

    def ejecutar(self) -> list[Usuario]:
        return self._usuarios.listar()
