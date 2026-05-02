"""Página de consulta de cajas nido."""

from dashboard.lib.ui import bloque_placeholder, encabezado_pagina


def render() -> None:
    """Renderiza la página de cajas nido."""
    encabezado_pagina(
        "Cajas nido",
        "Seguimiento de ocupación, huevos, pollos, ecosistemas, mapa y revisiones.",
        "🏡",
    )
    bloque_placeholder(
        "Revisiones de cajas nido",
        "En la Fase 6.4 se conectarán métricas, mapa, gráficos y fotos.",
    )
