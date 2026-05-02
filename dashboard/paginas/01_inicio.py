"""Página de inicio del dashboard."""

import streamlit as st

from dashboard.lib.ui import bloque_placeholder, encabezado_pagina, tarjeta_metrica


def render() -> None:
    """Renderiza la página de resumen inicial."""
    encabezado_pagina(
        "Dashboard fauna",
        "Vista rápida del sistema: visitas, especies, lugares y actividad reciente.",
        "🏠",
    )
    cols = st.columns(4)
    with cols[0]:
        tarjeta_metrica("Total visitas", "Pendiente")
    with cols[1]:
        tarjeta_metrica("Especies observadas", "Pendiente")
    with cols[2]:
        tarjeta_metrica("Cajas ocupadas", "Pendiente")
    with cols[3]:
        tarjeta_metrica("Capturas vv", "Pendiente")
    bloque_placeholder(
        "Resumen en preparación",
        "En la Fase 6.3 se conectarán métricas, gráficos y últimos registros reales.",
    )
