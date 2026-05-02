"""Página de consulta Lindus."""

from dashboard.lib.ui import bloque_placeholder, encabezado_pagina


def render() -> None:
    """Renderiza la página Lindus."""
    encabezado_pagina(
        "Lindus",
        "Consulta de observaciones migratorias, detalle, meteorología y fotos asociadas.",
        "🦅",
    )
    bloque_placeholder(
        "Observaciones Lindus",
        "En la Fase 6.4 se añadirán filtros, gráficos, tabla y panel de detalle.",
    )
