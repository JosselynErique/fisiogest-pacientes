"""Reglas de validación reutilizables (principio de reutilización del diseño)."""

from __future__ import annotations

import re
from datetime import date, datetime, time

_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")
_TELEFONO = re.compile(r"^0\d{8,9}$")


def limpiar(valor: str | None) -> str:
    """Quita espacios sobrantes (incluidos los dobles espacios internos)."""
    return " ".join((valor or "").split())


def es_cedula_valida(cedula: str) -> bool:
    """Valida una cédula ecuatoriana con el algoritmo del módulo 10."""
    if not re.fullmatch(r"\d{10}", cedula):
        return False
    provincia = int(cedula[:2])
    if not (1 <= provincia <= 24 or provincia == 30):
        return False
    if int(cedula[2]) >= 6:
        return False
    total = 0
    for digito, coeficiente in zip(cedula[:9], (2, 1, 2, 1, 2, 1, 2, 1, 2), strict=True):
        producto = int(digito) * coeficiente
        total += producto - 9 if producto > 9 else producto
    verificador = (10 - total % 10) % 10
    return verificador == int(cedula[9])


def es_correo_valido(correo: str) -> bool:
    return bool(_CORREO.match(correo))


def es_telefono_valido(telefono: str) -> bool:
    """Celular (09XXXXXXXX) o fijo con código de área (0XXXXXXXX)."""
    return bool(_TELEFONO.match(telefono))


def parsear_fecha(valor: str) -> date | None:
    try:
        return date.fromisoformat(valor)
    except (TypeError, ValueError):
        return None


def parsear_hora(valor: str) -> time | None:
    try:
        return datetime.strptime(valor, "%H:%M").time()
    except (TypeError, ValueError):
        return None


def parsear_entero(valor: str | int | None) -> int | None:
    try:
        return int(valor)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
