"""Entrada principal del dashboard Streamlit de BirdLog."""

from importlib import import_module
from pathlib import Path
import sys

import streamlit as st


RAIZ_PROYECTO = Path(__file__).resolve().parents[1]
if str(RAIZ_PROYECTO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROYECTO))

from dashboard.lib.conexion import probar_conexion
from dashboard.lib.ui import aplicar_estilos, encabezado_pagina, estado_conexion, render_sidebar


PAGINAS = {
    "Inicio": "dashboard.paginas.01_inicio",
    "Mapa general": "dashboard.paginas.02_mapa_general",
    "Lindus": "dashboard.paginas.03_lindus",
    "Cajas nido": "dashboard.paginas.04_cajas_nido",
    "Nidos rapaces": "dashboard.paginas.05_nidos_rapaces",
    "Cebos avispones": "dashboard.paginas.06_cebos_avispones",
    "Mamíferos puentes": "dashboard.paginas.07_mamiferos_puentes",
    "Edición / Catálogos": "dashboard.paginas.08_edicion",
}


def main() -> None:
    """Configura la aplicación y renderiza la página seleccionada."""
    st.set_page_config(
        page_title="BirdLog",
        page_icon="🌿",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    aplicar_estilos()

    pagina = render_sidebar(PAGINAS.keys())
    estado_conexion(probar_conexion())
    encabezado_pagina(pagina)
    modulo = import_module(PAGINAS[pagina])
    modulo.render()


if __name__ == "__main__":
    main()
