from __future__ import annotations

from fisiogest.shared.domain.errors import DomainError, NotFoundError
from fisiogest.usuarios.domain.ports import UsuarioRepository
from fisiogest.usuarios.domain.usuario import Rol, Usuario


class CambiarEstadoUsuario:
    def __init__(self, usuarios: UsuarioRepository) -> None:
        self._usuarios = usuarios

    def ejecutar(self, usuario_id: int, activo: bool, solicitante_id: int) -> Usuario:
        usuario = self._usuarios.obtener(usuario_id)
        if usuario is None:
            raise NotFoundError("El usuario no existe.")
        if usuario.id == solicitante_id:
            raise DomainError("No puede cambiar el estado de su propia cuenta.")
        if not activo and usuario.rol is Rol.ADMINISTRADOR:
            administradores = self._usuarios.listar(rol=Rol.ADMINISTRADOR, solo_activos=True)
            if len(administradores) <= 1:
                raise DomainError("Debe existir al menos un administrador activo.")
        usuario.activo = activo
        if activo:
            usuario.registrar_ingreso_exitoso()
        return self._usuarios.guardar(usuario)
