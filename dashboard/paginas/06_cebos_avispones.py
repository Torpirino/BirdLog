"""Página de consulta de cebos avispones."""

from dashboard.lib.ui import bloque_placeholder, encabezado_pagina


def render() -> None:
    """Renderiza la página de cebos avispones."""
    encabezado_pagina(
        "Cebos avispones",
        "Capturas por cebo, acumulados calculados, composición y evolución temporal.",
        "🪤",
    )
    bloque_placeholder(
        "Seguimiento de cebos",
        "En la Fase 6.4 se añadirán acumulados, ranking, mapas y tablas de revisiones.",
    )
