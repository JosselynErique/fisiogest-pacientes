"""Acceso a SQLite. Implementa el patrón Singleton definido en el diseño (Unidad 2):
existe una sola instancia de `Database` por archivo, que centraliza la configuración
de las conexiones y la creación del esquema.
"""

from __future__ import annotations

import sqlite3
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

_ESQUEMA = Path(__file__).with_name("schema.sql")


class Database:
    _instancias: dict[str, Database] = {}
    _lock = threading.Lock()

    def __new__(cls, ruta: str | Path) -> Database:
        clave = str(Path(ruta).resolve())
        with cls._lock:
            instancia = cls._instancias.get(clave)
            if instancia is None:
                instancia = super().__new__(cls)
                instancia._ruta = clave
                cls._instancias[clave] = instancia
            return instancia

    @property
    def ruta(self) -> str:
        return self._ruta

    @contextmanager
    def conexion(self) -> Iterator[sqlite3.Connection]:
        """Abre una conexión transaccional: confirma al salir, revierte si hay error."""
        con = sqlite3.connect(self._ruta)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys = ON")
        try:
            yield con
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    def inicializar(self) -> None:
        Path(self._ruta).parent.mkdir(parents=True, exist_ok=True)
        with self.conexion() as con:
            con.executescript(_ESQUEMA.read_text(encoding="utf-8"))
