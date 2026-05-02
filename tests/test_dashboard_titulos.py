"""Comprobaciones de títulos del dashboard."""

from __future__ import annotations

import ast
from pathlib import Path


TITULOS_ESPERADOS = {
    "dashboard/paginas/01_inicio.py": "Inicio",
    "dashboard/paginas/02_mapa_general.py": "Mapa general",
    "dashboard/paginas/03_lindus.py": "Lindus",
    "dashboard/paginas/04_cajas_nido.py": "Cajas nido",
    "dashboard/paginas/05_nidos_rapaces.py": "Nidos rapaces",
    "dashboard/paginas/06_cebos_avispones.py": "Cebos avispones",
    "dashboard/paginas/07_mamiferos_puentes.py": "Mamíferos puentes",
    "dashboard/paginas/08_edicion.py": "Edición / Catálogos",
}


def _titulos_encabezado(ruta: Path) -> list[str]:
    """Extrae llamadas literales a encabezado_pagina()."""
    arbol = ast.parse(ruta.read_text(encoding="utf-8"))
    titulos = []
    for nodo in ast.walk(arbol):
        if not isinstance(nodo, ast.Call):
            continue
        if getattr(nodo.func, "id", "") != "encabezado_pagina":
            continue
        if len(nodo.args) != 1:
            raise AssertionError(f"{ruta} debe pasar solo el título a encabezado_pagina()")
        titulo = nodo.args[0]
        if not isinstance(titulo, ast.Constant) or not isinstance(titulo.value, str):
            raise AssertionError(f"{ruta} debe usar un título literal y explícito")
        titulos.append(titulo.value)
    return titulos


def test_paginas_declaran_su_titulo_real() -> None:
    """Cada página muestra su propio título, sin heredar Inicio."""
    raiz = Path(__file__).resolve().parents[1]
    for ruta_relativa, esperado in TITULOS_ESPERADOS.items():
        titulos = _titulos_encabezado(raiz / ruta_relativa)
        assert titulos == [esperado]
