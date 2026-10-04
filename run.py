"""Punto de entrada para ejecutar FisioGest en local:

    python run.py

Crea la base de datos SQLite (instance/fisiogest.db) y, en modo demo, carga datos de ejemplo.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from fisiogest.app import create_app  # noqa: E402

app = create_app()

if __name__ == "__main__":
    puerto = int(os.environ.get("FISIOGEST_PORT", "5000"))
    host = os.environ.get("FISIOGEST_HOST", "127.0.0.1")
    print(
        f"FisioGest disponible en http://{'localhost' if host in ('127.0.0.1', '0.0.0.0') else host}:{puerto}"
    )
    app.run(host=host, port=puerto, debug=os.environ.get("FISIOGEST_DEBUG", "1") == "1")
