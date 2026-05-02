"""Página de inicio del dashboard."""

import altair as alt
import pandas as pd
import streamlit as st

from dashboard.lib.consultas import (
    cargar_tablas_dashboard,
    conteo_por,
    metricas_inicio,
    ranking_especies,
    ultimos_registros,
    visitas_legibles,
)
from dashboard.lib.graficos import grafico_barras, grafico_lineas, visitas_por_mes
from dashboard.lib.ui import bloque_grafico, encabezado_pagina, rejilla_metricas, separador_seccion, tabla_datos


@st.cache_data(ttl=120)
def _cargar_datos() -> dict[str, pd.DataFrame]:
    """Carga datos de portada con caché corta."""
    return cargar_tablas_dashboard()


def render() -> None:
    """Renderiza la página de resumen inicial."""
    encabezado_pagina(
        "Dashboard fauna",
        "Vista rápida del sistema: visitas, especies, lugares y actividad reciente.",
        "🏠",
    )
    try:
        tablas = _cargar_datos()
    except Exception as exc:
        st.warning(f"No se pudieron cargar datos: {exc}")
        return

    rejilla_metricas(metricas_inicio(tablas))
    _render_graficos(tablas)
    _render_ultimos_registros(tablas)


def _render_graficos(tablas: dict[str, pd.DataFrame]) -> None:
    """Dibuja gráficos principales."""
    visitas = visitas_legibles(tablas)
    col_izq, col_der = st.columns(2)
    with col_izq:
        _chart_o_vacio(visitas_por_mes(visitas), "mes", "visitas", "Visitas por mes", "lineas")
        _chart_o_vacio(ranking_especies(tablas), "especie", "registros", "Top especies")
    with col_der:
        _chart_o_vacio(conteo_por(visitas, "tipo_visita"), "tipo_visita", "total", "Visitas por tipo")
        _chart_o_vacio(_capturas_vv_por_fecha(tablas), "fecha", "vv", "Capturas vv por fecha", "lineas")


def _render_ultimos_registros(tablas: dict[str, pd.DataFrame]) -> None:
    """Muestra tabla de últimos registros."""
    separador_seccion("Últimos registros")
    tabla_datos(ultimos_registros(tablas), "Sin registros recientes.")


def _chart_o_vacio(df: pd.DataFrame, x: str, y: str, titulo: str, tipo: str = "barras") -> None:
    """Muestra gráfico o mensaje sin datos."""
    chart = None
    if not df.empty:
        chart = grafico_lineas(df, x, y, titulo="") if tipo == "lineas" else grafico_barras(df, x, y, titulo="")
    bloque_grafico(titulo, chart)


def _capturas_vv_por_fecha(tablas: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Calcula capturas vv por fecha de visita."""
    cebos = tablas.get("cebos_avispones", pd.DataFrame())
    visitas = visitas_legibles(tablas)
    if cebos.empty or "vv" not in cebos or visitas.empty:
        return pd.DataFrame(columns=["fecha", "vv"])
    datos = cebos.merge(visitas[["id_visita", "fecha"]], on="id_visita", how="left")
    datos["vv"] = pd.to_numeric(datos["vv"], errors="coerce").fillna(0)
    return datos.groupby("fecha", dropna=False)["vv"].sum().reset_index()
