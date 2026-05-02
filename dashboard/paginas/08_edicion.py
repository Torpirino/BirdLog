"""Página de edición y catálogos."""

from dashboard.lib.ui import bloque_info, bloque_placeholder, encabezado_pagina


def render() -> None:
    """Renderiza la página de edición."""
    encabezado_pagina(
        "Edición / Catálogos",
        "Altas, correcciones y borrado seguro con confirmación escrita.",
        "✏️",
    )
    bloque_info(
        "Esta página no hará cambios silenciosos. El borrado requerirá escribir BORRAR."
    )
    bloque_placeholder(
        "Edición segura",
        "En la Fase 6.5 se implementarán formularios, validaciones y borrado seguro.",
    )
