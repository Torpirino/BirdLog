"""Página de consulta de cebos avispones."""

import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from dashboard.lib.consultas import cargar_tablas_consulta, etiqueta_registro, observaciones_legibles
from dashboard.lib.filtros import filtrar_fecha, filtrar_lugar, filtrar_rango_numerico, filtrar_valores, opciones_unicas
from dashboard.lib.fotos import enlaces_drive, filtrar_fotos_asociadas
from dashboard.lib.graficos import acumulado, grafico_barras, grafico_donut, grafico_lineas
from dashboard.lib.mapas import mapa_lugares
from dashboard.lib.ui import bloque_grafico, encabezado_pagina, mostrar_enlaces_fotos, rejilla_metricas, sin_datos, tabla_datos


CAPTURAS = ["vv", "crabro", "avispa_europea", "polilla", "mariposa", "otros"]


@st.cache_data(ttl=120)
def _cargar_datos() -> dict[str, pd.DataFrame]:
    """Carga datos de cebos."""
    return cargar_tablas_consulta()


def render() -> None:
    """Renderiza la página de cebos avispones."""
    encabezado_pagina(
        "Cebos avispones",
        "Capturas por cebo, acumulados calculados, composición y evolución temporal.",
        "🪤",
    )
    try:
        tablas = _cargar_datos()
    except Exception as exc:
        st.warning(f"No se pudieron cargar datos: {exc}")
        return
    datos = observaciones_legibles("cebos_avispones", tablas)
    if datos.empty:
        sin_datos("Sin datos de cebos avispones todavía.")
        return
    datos = _normalizar_capturas(datos)
    filtrados = _render_filtros(datos)
    _render_metricas(filtrados)
    _render_graficos(filtrados)
    _render_mapa(filtrados)
    _render_tabla_y_detalle(filtrados, tablas)


def _render_filtros(datos: pd.DataFrame) -> pd.DataFrame:
    """Dibuja filtros de cebos."""
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        desde, hasta = _rango_fechas(c1, datos)
        lugares = c2.multiselect("Lugar / cebo", opciones_unicas(datos, "nombre_lugar"))
        municipios = c3.multiselect("Municipio", opciones_unicas(datos, "municipio"))
        vv_min, vv_max = _rango_vv(datos)
    filtrados = filtrar_fecha(datos, desde=desde, hasta=hasta)
    filtrados = filtrar_lugar(filtrados, lugares)
    filtrados = filtrar_valores(filtrados, "municipio", municipios)
    return filtrar_rango_numerico(filtrados, "vv", vv_min, vv_max)


def _render_metricas(datos: pd.DataFrame) -> None:
    """Muestra métricas de cebos."""
    vv = _suma(datos, "vv")
    crabro = _suma(datos, "crabro")
    otras = sum(_suma(datos, col) for col in ["avispa_europea", "polilla", "mariposa", "otros"])
    rejilla_metricas(
        [
            ("Revisiones", str(len(datos)) if len(datos) else "Sin datos", "Registros filtrados"),
            ("Total vv", str(vv) if vv else "Sin datos", "Vespa velutina"),
            ("Total crabro", str(crabro) if crabro else "Sin datos", "Vespa crabro"),
            ("Otras capturas", str(otras) if otras else "Sin datos", "Resto de capturas"),
        ]
    )


def _render_graficos(datos: pd.DataFrame) -> None:
    """Dibuja gráficos de cebos."""
    col1, col2 = st.columns(2)
    with col1:
        _grafico(_ranking_cebos(datos), "nombre_lugar", "vv", "Ranking de cebos")
        _grafico(_por_fecha(datos, "vv"), "fecha", "vv", "Evolución vv", "lineas")
        _grafico(acumulado(_por_fecha(datos, "vv"), "fecha", "vv"), "fecha", "acumulado", "Acumulado por periodo", "lineas")
    with col2:
        _grafico(_composicion(datos), "captura", "total", "Composición de capturas", "donut")
        _grafico(_por_fecha(datos, "crabro"), "fecha", "crabro", "Evolución crabro", "lineas")


def _render_mapa(datos: pd.DataFrame) -> None:
    """Muestra mapa de cebos."""
    st.subheader("Mapa de cebos")
    lugares = datos.drop_duplicates("id_lugar") if "id_lugar" in datos else pd.DataFrame()
    if lugares.empty:
        st.info("Sin coordenadas de cebos para los filtros.")
        return
    st_folium(mapa_lugares(lugares, "Cebos avispones"), use_container_width=True, height=460)


def _render_tabla_y_detalle(datos: pd.DataFrame, tablas: dict[str, pd.DataFrame]) -> None:
    """Tabla y detalle de revisión."""
    st.subheader("Revisiones")
    columnas = ["id_cebo", "fecha", "nombre_lugar", "municipio", *CAPTURAS, "observaciones"]
    tabla_datos(datos[[c for c in columnas if c in datos]], "Sin revisiones para los filtros.")
    if datos.empty:
        return
    seleccion = st.selectbox(
        "Detalle de revisión",
        datos.index,
        format_func=lambda idx: etiqueta_registro(datos.loc[idx], "id_cebo", ["fecha", "nombre_lugar", "vv"]),
    )
    registro = datos.loc[seleccion]
    with st.container(border=True):
        st.subheader("Detalle")
        st.write(registro[[c for c in columnas if c in registro.index]].to_dict())
        st.caption("Fotos asociadas")
        fotos = filtrar_fotos_asociadas(tablas.get("fotos", pd.DataFrame()), registro.get("id_visita"), "cebos_avispones", registro.get("id_cebo"))
        mostrar_enlaces_fotos(enlaces_drive(fotos))


def _grafico(df: pd.DataFrame, x: str, y: str, titulo: str, tipo: str = "barras") -> None:
    """Muestra gráfico o aviso."""
    chart = None
    if not df.empty:
        if tipo == "lineas":
            chart = grafico_lineas(df, x, y)
        elif tipo == "donut":
            chart = grafico_donut(df, x, y)
        else:
            chart = grafico_barras(df, x, y)
    bloque_grafico(titulo, chart)


def _normalizar_capturas(datos: pd.DataFrame) -> pd.DataFrame:
    """Convierte capturas a numérico."""
    copia = datos.copy()
    for columna in CAPTURAS:
        if columna in copia:
            copia[columna] = pd.to_numeric(copia[columna], errors="coerce").fillna(0)
    return copia


def _ranking_cebos(datos: pd.DataFrame) -> pd.DataFrame:
    """Suma vv por cebo."""
    if datos.empty or "nombre_lugar" not in datos:
        return pd.DataFrame(columns=["nombre_lugar", "vv"])
    return datos.groupby("nombre_lugar")["vv"].sum().reset_index().sort_values("vv", ascending=False)


def _por_fecha(datos: pd.DataFrame, columna: str) -> pd.DataFrame:
    """Suma capturas por fecha."""
    if datos.empty or columna not in datos or "fecha" not in datos:
        return pd.DataFrame(columns=["fecha", columna])
    return datos.groupby("fecha")[columna].sum().reset_index()


def _composicion(datos: pd.DataFrame) -> pd.DataFrame:
    """Calcula composición de capturas."""
    return pd.DataFrame({"captura": CAPTURAS, "total": [_suma(datos, col) for col in CAPTURAS]})


def _suma(datos: pd.DataFrame, columna: str) -> int:
    """Suma columna."""
    if datos.empty or columna not in datos:
        return 0
    return int(pd.to_numeric(datos[columna], errors="coerce").fillna(0).sum())


def _rango_fechas(columna, datos: pd.DataFrame):
    """Selector de fechas."""
    fechas = pd.to_datetime(datos["fecha"], errors="coerce").dropna().dt.date
    if fechas.empty:
        return None, None
    rango = columna.date_input("Fecha", value=(fechas.min(), fechas.max()), key="cebos_fecha")
    return rango if isinstance(rango, tuple) and len(rango) == 2 else (None, None)


def _rango_vv(datos: pd.DataFrame) -> tuple[int, int]:
    """Selector robusto para rango de vv."""
    minimo, maximo = int(datos["vv"].min()), int(datos["vv"].max())
    if minimo == maximo:
        st.caption(f"Rango vv: {minimo}")
        return minimo, maximo
    return st.slider("Rango vv", minimo, maximo, (minimo, maximo))
