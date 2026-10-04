"""RF-09: inicio de sesión de usuarios según su rol."""

from __future__ import annotations

import math
from collections.abc import Callable
from datetime import datetime

from fisiogest.shared.domain.errors import AuthenticationError
from fisiogest.usuarios.domain.ports import PasswordHasher, UsuarioRepository
from fisiogest.usuarios.domain.usuario import Usuario

MENSAJE_GENERICO = "Usuario o contraseña incorrectos."


class IniciarSesion:
    def __init__(
        self,
        usuarios: UsuarioRepository,
        hasher: PasswordHasher,
        reloj: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._usuarios = usuarios
        self._hasher = hasher
        self._reloj = reloj

    def ejecutar(self, username: str, password: str) -> Usuario:
        ahora = self._reloj()
        usuario = self._usuarios.obtener_por_username(username.strip().lower())
        if usuario is None or not usuario.activo:
            raise AuthenticationError(MENSAJE_GENERICO)
        if usuario.esta_bloqueado(ahora):
            minutos = math.ceil((usuario.bloqueado_hasta - ahora).total_seconds() / 60)
            raise AuthenticationError(
                f"Cuenta bloqueada temporalmente por intentos fallidos. Intente en {minutos} min."
            )
        if not self._hasher.verificar(usuario.password_hash, password):
            usuario.registrar_intento_fallido(ahora)
            self._usuarios.guardar(usuario)
            raise AuthenticationError(MENSAJE_GENERICO)
        usuario.registrar_ingreso_exitoso()
        self._usuarios.guardar(usuario)
        return usuario
