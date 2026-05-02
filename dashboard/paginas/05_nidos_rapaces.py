"""Página de consulta de nidos de rapaces."""

from dashboard.lib.ui import bloque_placeholder, encabezado_pagina


def render() -> None:
    """Renderiza la página de nidos rapaces."""
    encabezado_pagina(
        "Nidos rapaces",
        "Histórico de revisiones, localización real, texto de campo y fotos.",
        "🪶",
    )
    bloque_placeholder(
        "Histórico de nidos",
        "En la Fase 6.4 se añadirá lectura cómoda por nido, filtros y mapa específico.",
    )
