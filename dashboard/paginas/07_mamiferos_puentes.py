"""Página de consulta de mamíferos en puentes."""

from dashboard.lib.ui import bloque_placeholder, encabezado_pagina


def render() -> None:
    """Renderiza la página de mamíferos puentes."""
    encabezado_pagina(
        "Mamíferos puentes",
        "Preferencias espaciales por especie, presencia, evidencias y diversidad por puente.",
        "🐾",
    )
    bloque_placeholder(
        "Detecciones de mamíferos",
        "En la Fase 6.4 se añadirán selector de especie, mapa, rankings y fotos.",
    )
