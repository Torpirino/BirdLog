"""Página de mapa general."""

from datetime import date

import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from dashboard.lib.consultas import cargar_tablas_dashboard, lugares_con_actividad
from dashboard.lib.filtros import filtrar_valores, opciones_unicas
from dashboard.lib.mapas import mapa_lugares_por_tipo
from dashboard.lib.ui import encabezado_pagina, panel_filtros, tabla_datos


TIPOS_LUGAR = [
    "CONTEO_MIGRATORIO",
    "CAJA_NIDO",
    "CEBO_AVISPON",
    "NIDO_RAPAZ",
    "PUENTE",
]
ETIQUETAS_TIPO_LUGAR = {
    "CONTEO_MIGRATORIO": "Conteo migratorio",
    "CAJA_NIDO": "Cajas nido",
    "CEBO_AVISPON": "Cebos avispones",
    "NIDO_RAPAZ": "Nidos rapaces",
    "PUENTE": "Puentes",
}


@st.cache_data(ttl=120)
def _cargar_datos() -> dict[str, pd.DataFrame]:
    """Carga datos del mapa con caché corta."""
    return cargar_tablas_dashboard()


def render() -> None:
    """Renderiza el mapa general."""
    encabezado_pagina("Mapa general")
    try:
        tablas = _cargar_datos()
    except Exception as exc:
        st.warning(f"No se pudieron cargar datos: {exc}")
        return

    filtros = _render_filtros(tablas)
    lugares = _aplicar_filtros(tablas, filtros)
    _render_mapa(lugares)
    _render_tabla_lugares(lugares)


def _render_filtros(tablas: dict[str, pd.DataFrame]) -> dict[str, object]:
    """Dibuja filtros principales del mapa."""
    lugares = tablas.get("lugares", pd.DataFrame())
    especies = tablas.get("especies", pd.DataFrame())
    with panel_filtros():
        tipos = _checkboxes_tipo_lugar(lugares)
        col_municipio, col_especie, col_fecha = st.columns(3)
        municipios = col_municipio.multiselect("Municipio", opciones_unicas(lugares, "municipio"))
        especies_sel = col_especie.multiselect("Especie asociada", _opciones_especies(especies))
        desde, hasta = _selector_fechas(col_fecha, tablas.get("visitas", pd.DataFrame()))
    return {"tipos": tipos, "municipios": municipios, "especies": especies_sel, "desde": desde, "hasta": hasta}


def _aplicar_filtros(tablas: dict[str, pd.DataFrame], filtros: dict[str, object]) -> pd.DataFrame:
    """Aplica filtros de actividad, tipo y municipio."""
    lugares = lugares_con_actividad(
        tablas,
        desde=filtros["desde"],
        hasta=filtros["hasta"],
        especies=filtros["especies"],
    )
    if not filtros["tipos"]:
        return lugares.iloc[0:0]
    lugares = filtrar_valores(lugares, "tipo_lugar", filtros["tipos"])
    return filtrar_valores(lugares, "municipio", filtros["municipios"])


def _render_mapa(lugares: pd.DataFrame) -> None:
    """Dibuja mapa o aviso si no hay coordenadas."""
    if lugares.empty:
        st.info("Sin lugares para los filtros seleccionados.")
        return
    mapa = mapa_lugares_por_tipo(lugares)
    st_folium(mapa, use_container_width=True, height=560)


def _render_tabla_lugares(lugares: pd.DataFrame) -> None:
    """Muestra tabla con coordenadas visibles."""
    st.subheader("Lugares en el mapa")
    columnas = ["nombre_lugar", "tipo_lugar", "municipio", "utm_x", "utm_y"]
    tabla = lugares[[c for c in columnas if c in lugares.columns]] if not lugares.empty else lugares
    tabla_datos(tabla, "Sin lugares para mostrar.")


def _checkboxes_tipo_lugar(lugares: pd.DataFrame) -> list[str]:
    """Dibuja tipos de lugar como checkboxes visibles."""
    disponibles = set(opciones_unicas(lugares, "tipo_lugar"))
    st.markdown("**Tipo de lugar**")
    columnas = st.columns(len(TIPOS_LUGAR))
    seleccionados = []
    for columna, tipo in zip(columnas, TIPOS_LUGAR, strict=False):
        valor_inicial = tipo in disponibles or not disponibles
        marcado = columna.checkbox(
            ETIQUETAS_TIPO_LUGAR[tipo],
            value=valor_inicial,
            key=f"mapa_tipo_lugar_{tipo}",
        )
        if marcado:
            seleccionados.append(tipo)
    return seleccionados


def _selector_fechas(columna, visitas: pd.DataFrame) -> tuple[date | None, date | None]:
    """Dibuja selector de rango si existen fechas."""
    if visitas.empty or "fecha" not in visitas.columns:
        return None, None
    fechas = pd.to_datetime(visitas["fecha"], errors="coerce").dropna().dt.date
    if fechas.empty:
        return None, None
    rango = columna.date_input("Rango de fechas", value=(fechas.min(), fechas.max()))
    return rango if isinstance(rango, tuple) and len(rango) == 2 else (None, None)


def _opciones_especies(especies: pd.DataFrame) -> list[str]:
    """Devuelve nombres de especies para filtros."""
    if especies.empty:
        return []
    columna = "nombre_comun" if "nombre_comun" in especies else "nombre_cientifico"
    return especies[columna].dropna().astype(str).sort_values().unique().tolist()
