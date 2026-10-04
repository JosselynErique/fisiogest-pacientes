"""Constantes y utilidades compartidas por las pruebas."""

from __future__ import annotations

from datetime import datetime

# Lunes 5 de octubre de 2026, 08:00. Un reloj fijo hace deterministas las pruebas.
AHORA = datetime(2026, 10, 5, 8, 0)
PASSWORD = "Prueba2026"

# Cédulas sintéticas válidas (dígito verificador correcto) para las pruebas.
CEDULA_1 = "1722601810"
CEDULA_2 = "1129083018"
CEDULA_3 = "1636131862"


def obtener_csrf(cliente) -> str:
    """Obtiene el token CSRF de la sesión (se genera al renderizar cualquier página)."""
    with cliente.session_transaction() as sesion:
        token = sesion.get("_csrf")
    if token is None:
        cliente.get("/login")
        cliente.get("/")
        with cliente.session_transaction() as sesion:
            token = sesion["_csrf"]
    return token


def iniciar_sesion(cliente, username: str, password: str = PASSWORD):
    token = obtener_csrf(cliente)
    return cliente.post("/login", data={"username": username, "password": password, "_csrf": token})
