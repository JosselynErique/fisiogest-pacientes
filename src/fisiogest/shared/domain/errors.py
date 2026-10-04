"""Errores de dominio compartidos por todos los módulos.

Los casos de uso lanzan estas excepciones; los adaptadores de entrada (HTTP)
las traducen a respuestas para el usuario. El dominio nunca conoce Flask.
"""

from __future__ import annotations


class DomainError(Exception):
    """Se violó una regla de negocio. El mensaje es apto para mostrar al usuario."""


class ValidationError(DomainError):
    """Uno o más campos tienen datos inválidos."""

    def __init__(self, errores: dict[str, str]):
        self.errores = errores
        super().__init__(" ".join(errores.values()))


class NotFoundError(DomainError):
    """El recurso solicitado no existe."""


class ConflictError(DomainError):
    """La operación entra en conflicto con el estado actual (duplicados, choques de horario...)."""


class AuthenticationError(DomainError):
    """Credenciales inválidas o cuenta bloqueada."""


class Errores:
    """Acumula errores de validación por campo para informarlos todos a la vez."""

    def __init__(self) -> None:
        self._errores: dict[str, str] = {}

    def agregar(self, campo: str, mensaje: str) -> None:
        self._errores.setdefault(campo, mensaje)

    def lanzar_si_hay(self) -> None:
        if self._errores:
            raise ValidationError(dict(self._errores))
