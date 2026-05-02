"""Comprobaciones de títulos del dashboard."""

from __future__ import annotations

import ast
from pathlib import Path


TITULOS_ESPERADOS = [
    "Inicio",
    "Mapa general",
    "Lindus",
    "Cajas nido",
    "Nidos rapaces",
    "Cebos avispones",
    "Mamíferos puentes",
    "Edición / Catálogos",
]


def _llamadas_encabezado(ruta: Path) -> list[ast.Call]:
    """Extrae llamadas a encabezado_pagina()."""
    arbol = ast.parse(ruta.read_text(encoding="utf-8"))
    llamadas = []
    for nodo in ast.walk(arbol):
        if not isinstance(nodo, ast.Call):
            continue
        if getattr(nodo.func, "id", "") != "encabezado_pagina":
            continue
        llamadas.append(nodo)
    return llamadas


def test_app_define_titulos_del_menu() -> None:
    """El menú lateral contiene los títulos visibles de las páginas."""
    from dashboard.app import PAGINAS

    assert list(PAGINAS) == TITULOS_ESPERADOS


def test_app_pinta_titulo_desde_pagina_seleccionada() -> None:
    """La cabecera sale de la opción activa del menú lateral."""
    raiz = Path(__file__).resolve().parents[1]
    llamadas = _llamadas_encabezado(raiz / "dashboard/app.py")
    assert len(llamadas) == 1
    assert len(llamadas[0].args) == 1
    assert isinstance(llamadas[0].args[0], ast.Name)
    assert llamadas[0].args[0].id == "pagina"


def test_sidebar_no_usa_radio_para_navegar() -> None:
    """La navegación no depende de un radio con estado persistente."""
    contenido = (Path(__file__).resolve().parents[1] / "dashboard/lib/ui.py").read_text(
        encoding="utf-8"
    )
    assert "st.radio" not in contenido
    assert 'st.session_state["pagina_activa"]' in contenido
    assert "st.rerun()" in contenido


def test_paginas_no_pintan_cabecera_propia() -> None:
    """Las páginas no pueden heredar accidentalmente una cabecera fija."""
    raiz = Path(__file__).resolve().parents[1]
    for ruta in (raiz / "dashboard/paginas").glob("*.py"):
        assert _llamadas_encabezado(ruta) == []
