"""Página de mapa general."""

from dashboard.lib.ui import bloque_placeholder, encabezado_pagina


def render() -> None:
    """Renderiza el mapa general."""
    encabezado_pagina(
        "Mapa general",
        "Capas activables para cajas nido, rapaces, cebos, puentes y puntos Lindus.",
        "🗺️",
    )
    bloque_placeholder(
        "Mapa general",
        "En la Fase 6.3 se añadirá el mapa folium con filtros por tipo, municipio y fechas.",
    )
