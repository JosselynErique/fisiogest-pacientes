from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from fisiogest.shared.domain.errors import Errores
from fisiogest.shared.domain.validators import limpiar

_USERNAME = re.compile(r"^[a-z0-9._]{3,30}$")


class Rol(str, Enum):
    ADMINISTRADOR = "administrador"
    RECEPCIONISTA = "recepcionista"
    FISIOTERAPEUTA = "fisioterapeuta"

    @property
    def etiqueta(self) -> str:
        return self.value.capitalize()


@dataclass(frozen=True)
class DatosUsuario:
    username: str
    nombre_completo: str
    rol: str
    password: str


def validar_password(password: str, errores: Errores, campo: str = "password") -> None:
    if len(password) < 8 or not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        errores.agregar(campo, "La contraseña debe tener al menos 8 caracteres, letras y números.")


@dataclass
class Usuario:
    username: str
    nombre_completo: str
    rol: Rol
    password_hash: str
    activo: bool = True
    intentos_fallidos: int = 0
    bloqueado_hasta: datetime | None = None
    id: int | None = None
    creado_en: datetime = field(default_factory=lambda: datetime.now().replace(microsecond=0))

    MAX_INTENTOS = 5
    MINUTOS_BLOQUEO = 10

    @classmethod
    def validar(cls, datos: DatosUsuario) -> tuple[str, str, Rol]:
        errores = Errores()
        username = limpiar(datos.username).lower()
        nombre = limpiar(datos.nombre_completo)
        if not _USERNAME.match(username):
            errores.agregar(
                "username",
                "El usuario debe tener 3 a 30 caracteres: letras, números, punto o guion bajo.",
            )
        if len(nombre) < 3:
            errores.agregar("nombre_completo", "Ingrese el nombre completo.")
        try:
            rol = Rol(datos.rol)
        except ValueError:
            errores.agregar("rol", "Seleccione un rol válido.")
            rol = Rol.RECEPCIONISTA
        validar_password(datos.password, errores)
        errores.lanzar_si_hay()
        return username, nombre, rol

    def tiene_rol(self, *roles: Rol) -> bool:
        return self.rol in roles

    def esta_bloqueado(self, ahora: datetime) -> bool:
        return self.bloqueado_hasta is not None and ahora < self.bloqueado_hasta

    def registrar_intento_fallido(self, ahora: datetime) -> None:
        self.intentos_fallidos += 1
        if self.intentos_fallidos >= self.MAX_INTENTOS:
            self.bloqueado_hasta = ahora + timedelta(minutes=self.MINUTOS_BLOQUEO)
            self.intentos_fallidos = 0

    def registrar_ingreso_exitoso(self) -> None:
        self.intentos_fallidos = 0
        self.bloqueado_hasta = None
