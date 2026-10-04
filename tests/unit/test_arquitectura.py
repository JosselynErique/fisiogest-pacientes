"""Verifica automáticamente las reglas de la arquitectura hexagonal.

- El dominio no depende de frameworks ni de infraestructura.
- Los casos de uso dependen solo de puertos: no importan Flask, SQLite ni adaptadores.
- Cada slice vertical contiene su caso de uso y su endpoint.
"""

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

RAIZ = Path(__file__).resolve().parents[2] / "src" / "fisiogest"
MODULOS = ["usuarios", "pacientes", "citas", "terapias", "historial", "reportes", "panel"]
PROHIBIDOS_EN_NUCLEO = (
    "flask",
    "werkzeug",
    "sqlite3",
    "fisiogest.shared.infrastructure",
    ".adapters",
)


def importaciones(archivo: Path) -> set[str]:
    arbol = ast.parse(archivo.read_text(encoding="utf-8"))
    nombres = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            nombres.update(alias.name for alias in nodo.names)
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            nombres.add(nodo.module)
    return nombres


def archivos_del_nucleo() -> list[Path]:
    dominio = [p for p in RAIZ.glob("*/domain/*.py")]
    casos_de_uso = list(RAIZ.glob("*/features/*/caso_uso.py"))
    return dominio + casos_de_uso


@pytest.mark.parametrize("archivo", archivos_del_nucleo(), ids=lambda p: str(p.relative_to(RAIZ)))
def test_el_nucleo_no_depende_de_infraestructura(archivo):
    for nombre in importaciones(archivo):
        assert not any(
            nombre == p or nombre.startswith(p + ".") or p in nombre for p in PROHIBIDOS_EN_NUCLEO
        ), f"{archivo.relative_to(RAIZ)} importa {nombre}"


@pytest.mark.parametrize("modulo", MODULOS)
def test_cada_slice_tiene_su_endpoint(modulo):
    slices = [
        p for p in (RAIZ / modulo / "features").iterdir() if p.is_dir() and p.name != "__pycache__"
    ]
    assert slices, f"el módulo {modulo} no tiene slices"
    for carpeta in slices:
        assert (carpeta / "endpoint.py").exists(), f"falta endpoint.py en {carpeta.name}"


def test_los_adaptadores_solo_se_instancian_en_la_raiz_de_composicion():
    for archivo in RAIZ.rglob("*.py"):
        if "adapters" in archivo.parts or archivo.name == "container.py":
            continue
        for nombre in importaciones(archivo):
            assert ".adapters." not in nombre, f"{archivo.relative_to(RAIZ)} importa {nombre}"
