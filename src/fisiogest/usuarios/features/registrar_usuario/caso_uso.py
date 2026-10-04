"""El administrador registra cuentas para el personal del consultorio."""

from __future__ import annotations

from fisiogest.shared.domain.errors import ConflictError
from fisiogest.usuarios.domain.ports import PasswordHasher, UsuarioRepository
from fisiogest.usuarios.domain.usuario import DatosUsuario, Usuario


class RegistrarUsuario:
    def __init__(self, usuarios: UsuarioRepository, hasher: PasswordHasher) -> None:
        self._usuarios = usuarios
        self._hasher = hasher

    def ejecutar(self, datos: DatosUsuario) -> Usuario:
        username, nombre, rol = Usuario.validar(datos)
        if self._usuarios.obtener_por_username(username):
            raise ConflictError(f"El usuario «{username}» ya existe.")
        usuario = Usuario(
            username=username,
            nombre_completo=nombre,
            rol=rol,
            password_hash=self._hasher.hashear(datos.password),
        )
        return self._usuarios.guardar(usuario)
