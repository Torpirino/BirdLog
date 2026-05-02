"""Página de consulta de cajas nido."""

import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from dashboard.lib.consultas import cargar_tablas_consulta, etiqueta_registro, observaciones_legibles, sumar_por
from dashboard.lib.filtros import filtrar_fecha, filtrar_lugar, filtrar_valores, opciones_unicas
from dashboard.lib.fotos import enlaces_drive, filtrar_fotos_asociadas
from dashboard.lib.graficos import grafico_barras, grafico_lineas
from dashboard.lib.mapas import mapa_lugares
from dashboard.lib.ui import bloque_grafico, encabezado_pagina, mostrar_enlaces_fotos, panel_filtros, rejilla_metricas, sin_datos, tabla_datos


@st.cache_data(ttl=120)
def _cargar_datos() -> dict[str, pd.DataFrame]:
    """Carga datos de cajas nido."""
    return cargar_tablas_consulta()


def render() -> None:
    """Renderiza la página de cajas nido."""
    encabezado_pagina(
        "Cajas nido",
        "Seguimiento de ocupación, huevos, pollos, ecosistemas, mapa y revisiones.",
        "🏡",
    )
    try:
        tablas = _cargar_datos()
    except Exception as exc:
        st.warning(f"No se pudieron cargar datos: {exc}")
        return
    datos = observaciones_legibles("cajas_nido", tablas)
    if datos.empty:
        sin_datos("Sin datos de cajas nido todavía.")
        return
    filtrados = _render_filtros(datos)
    _render_metricas(filtrados)
    _render_graficos(filtrados)
    _render_mapa(filtrados)
    _render_tabla_y_detalle(filtrados, tablas)


def _render_filtros(datos: pd.DataFrame) -> pd.DataFrame:
    """Dibuja filtros de cajas."""
    with panel_filtros():
        c1, c2, c3 = st.columns(3)
        desde, hasta = _rango_fechas(c1, datos)
        lugares = c2.multiselect("Lugar / caja", opciones_unicas(datos, "nombre_lugar"))
        especies = c3.multiselect("Especie", opciones_unicas(datos, "nombre_comun"))
        c4, c5, c6 = st.columns(3)
        ecosistemas = c4.multiselect("Ecosistema", opciones_unicas(datos, "ecosistema"))
        estados = c5.multiselect("Estado nido", opciones_unicas(datos, "estado_nido"))
        ocupada = c6.selectbox("Ocupada", ["Todas", "Sí", "No"])
    filtrados = filtrar_fecha(datos, desde=desde, hasta=hasta)
    filtrados = filtrar_lugar(filtrados, lugares)
    filtrados = filtrar_valores(filtrados, "nombre_comun", especies)
    filtrados = filtrar_valores(filtrados, "ecosistema", ecosistemas)
    filtrados = filtrar_valores(filtrados, "estado_nido", estados)
    if ocupada != "Todas" and "ocupada" in filtrados:
        filtrados = filtrados[filtrados["ocupada"].astype(bool) == (ocupada == "Sí")]
    return filtrados


def _render_metricas(datos: pd.DataFrame) -> None:
    """Muestra métricas de cajas."""
    ocupadas = int(datos["ocupada"].fillna(False).astype(bool).sum()) if "ocupada" in datos else 0
    total = len(datos)
    porcentaje = f"{(ocupadas / total * 100):.0f}%" if total else "Sin datos"
    huevos = _suma(datos, "numero_huevos")
    pollos = _suma(datos, "numero_pollos")
    rejilla_metricas(
        [
            ("Cajas revisadas", str(total) if total else "Sin datos", "Revisiones filtradas"),
            ("Cajas ocupadas", str(ocupadas) if ocupadas else "Sin datos", "Revisiones ocupadas"),
            ("Ocupación", porcentaje, "Porcentaje de revisiones ocupadas"),
            ("Huevos / pollos", f"{huevos} / {pollos}", "Totales filtrados"),
        ]
    )


def _render_graficos(datos: pd.DataFrame) -> None:
    """Dibuja gráficos de cajas."""
    col1, col2 = st.columns(2)
    with col1:
        _grafico(_ocupacion_por(datos, "ecosistema"), "ecosistema", "ocupadas", "Ocupación por ecosistema")
        _grafico(sumar_por(datos, "nombre_lugar", "numero_huevos", "huevos"), "nombre_lugar", "huevos", "Huevos por caja")
    with col2:
        _grafico(_conteo(datos, "estado_nido"), "estado_nido", "total", "Estado del nido")
        _grafico(_evolucion(datos), "fecha", "revisiones", "Evolución por fecha", "lineas")
        _grafico(sumar_por(datos, "nombre_lugar", "numero_pollos", "pollos"), "nombre_lugar", "pollos", "Pollos por caja")


def _render_mapa(datos: pd.DataFrame) -> None:
    """Muestra mapa de cajas."""
    st.subheader("Mapa de cajas")
    lugares = datos.drop_duplicates("id_lugar") if "id_lugar" in datos else pd.DataFrame()
    if lugares.empty:
        st.info("Sin coordenadas de cajas para los filtros.")
        return
    st_folium(mapa_lugares(lugares, "Cajas nido"), use_container_width=True, height=460)


def _render_tabla_y_detalle(datos: pd.DataFrame, tablas: dict[str, pd.DataFrame]) -> None:
    """Tabla y detalle de revisión."""
    st.subheader("Revisiones")
    columnas = ["id_cajanido", "fecha", "nombre_lugar", "ocupada", "numero_huevos", "numero_pollos", "ecosistema", "estado_nido"]
    tabla_datos(datos[[c for c in columnas if c in datos]], "Sin revisiones para los filtros.")
    if datos.empty:
        return
    seleccion = st.selectbox(
        "Detalle de revisión",
        datos.index,
        format_func=lambda idx: etiqueta_registro(datos.loc[idx], "id_cajanido", ["fecha", "nombre_lugar", "ocupada"]),
    )
    registro = datos.loc[seleccion]
    with st.container(border=True):
        st.subheader("Detalle")
        st.write(registro.to_dict())
        st.caption("Fotos asociadas")
        fotos = filtrar_fotos_asociadas(tablas.get("fotos", pd.DataFrame()), registro.get("id_visita"), "cajas_nido", registro.get("id_cajanido"))
        mostrar_enlaces_fotos(enlaces_drive(fotos))


def _grafico(df: pd.DataFrame, x: str, y: str, titulo: str, tipo: str = "barras") -> None:
    """Muestra gráfico o aviso."""
    chart = None
    if not df.empty:
        chart = grafico_lineas(df, x, y) if tipo == "lineas" else grafico_barras(df, x, y)
    bloque_grafico(titulo, chart)


def _rango_fechas(columna, datos: pd.DataFrame):
    """Selector de fechas."""
    fechas = pd.to_datetime(datos["fecha"], errors="coerce").dropna().dt.date
    if fechas.empty:
        return None, None
    rango = columna.date_input("Fecha", value=(fechas.min(), fechas.max()), key="cajas_fecha")
    return rango if isinstance(rango, tuple) and len(rango) == 2 else (None, None)


def _suma(datos: pd.DataFrame, columna: str) -> int:
    """Suma columna numérica."""
    if datos.empty or columna not in datos:
        return 0
    return int(pd.to_numeric(datos[columna], errors="coerce").fillna(0).sum())


def _ocupacion_por(datos: pd.DataFrame, columna: str) -> pd.DataFrame:
    """Cuenta ocupadas por grupo."""
    if datos.empty or columna not in datos or "ocupada" not in datos:
        return pd.DataFrame(columns=[columna, "ocupadas"])
    copia = datos.copy()
    copia["ocupadas"] = copia["ocupada"].fillna(False).astype(bool).astype(int)
    return copia.groupby(columna)["ocupadas"].sum().reset_index()


def _conteo(datos: pd.DataFrame, columna: str) -> pd.DataFrame:
    """Cuenta filas por columna."""
    if datos.empty or columna not in datos:
        return pd.DataFrame(columns=[columna, "total"])
    return datos.groupby(columna).size().reset_index(name="total")


def _evolucion(datos: pd.DataFrame) -> pd.DataFrame:
    """Cuenta revisiones por fecha."""
    if datos.empty or "fecha" not in datos:
        return pd.DataFrame(columns=["fecha", "revisiones"])
    return datos.groupby("fecha").size().reset_index(name="revisiones")
