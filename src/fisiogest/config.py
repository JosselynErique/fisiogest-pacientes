"""Configuración leída del entorno (y de un archivo .env opcional en la raíz)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

RAIZ_PROYECTO = Path(__file__).resolve().parents[2]


def cargar_dotenv(ruta: Path = RAIZ_PROYECTO / ".env") -> None:
    """Lector mínimo de .env para no añadir dependencias. No pisa variables ya definidas."""
    if not ruta.exists():
        return
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        os.environ.setdefault(clave.strip(), valor.strip().strip('"').strip("'"))


@dataclass(frozen=True)
class Config:
    secret_key: str
    database: Path
    demo: bool
    testing: bool = False

    @classmethod
    def desde_entorno(cls) -> Config:
        cargar_dotenv()
        database = Path(os.environ.get("FISIOGEST_DATABASE", "instance/fisiogest.db"))
        if not database.is_absolute():
            database = RAIZ_PROYECTO / database
        return cls(
            secret_key=os.environ.get("FISIOGEST_SECRET_KEY", "clave-de-desarrollo-fisiogest"),
            database=database,
            demo=os.environ.get("FISIOGEST_DEMO", "1") == "1",
        )
