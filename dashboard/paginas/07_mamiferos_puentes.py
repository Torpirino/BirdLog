"""Página de consulta de mamíferos en puentes."""

import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from dashboard.lib.consultas import cargar_tablas_consulta, etiqueta_registro, observaciones_legibles
from dashboard.lib.filtros import filtrar_fecha, filtrar_lugar, filtrar_valores, opciones_unicas
from dashboard.lib.fotos import enlaces_drive, filtrar_fotos_asociadas
from dashboard.lib.graficos import grafico_barras
from dashboard.lib.mapas import mapa_lugares
from dashboard.lib.ui import bloque_grafico, mostrar_enlaces_fotos, panel_filtros, rejilla_metricas, sin_datos, tabla_datos


@st.cache_data(ttl=120)
def _cargar_datos() -> dict[str, pd.DataFrame]:
    """Carga datos de mamíferos."""
    return cargar_tablas_consulta()


def render() -> None:
    """Renderiza la página de mamíferos puentes."""
    try:
        tablas = _cargar_datos()
    except Exception as exc:
        st.warning(f"No se pudieron cargar datos: {exc}")
        return
    datos = observaciones_legibles("mamiferos_puentes", tablas)
    if datos.empty:
        sin_datos("Sin datos de mamíferos en puentes todavía.")
        return
    filtrados = _render_filtros(datos)
    _render_metricas(filtrados)
    _render_graficos(filtrados)
    _render_mapa(filtrados)
    _render_tabla_y_detalle(filtrados, tablas)


def _render_filtros(datos: pd.DataFrame) -> pd.DataFrame:
    """Dibuja filtros de mamíferos."""
    with panel_filtros():
        c1, c2, c3 = st.columns(3)
        desde, hasta = _rango_fechas(c1, datos)
        especies = c2.multiselect("Especie", opciones_unicas(datos, "nombre_comun"))
        lugares = c3.multiselect("Puente", opciones_unicas(datos, "nombre_lugar"))
        c4, c5 = st.columns(2)
        presencias = c4.multiselect("Presencia", opciones_unicas(datos, "presencia"))
        evidencias = c5.multiselect("Tipo de evidencia", opciones_unicas(datos, "tipo_evidencia"))
    filtrados = filtrar_fecha(datos, desde=desde, hasta=hasta)
    filtrados = filtrar_valores(filtrados, "nombre_comun", especies)
    filtrados = filtrar_lugar(filtrados, lugares)
    filtrados = filtrar_valores(filtrados, "presencia", presencias)
    return filtrar_valores(filtrados, "tipo_evidencia", evidencias)


def _render_metricas(datos: pd.DataFrame) -> None:
    """Métricas de mamíferos."""
    especies = datos["id_especie"].nunique() if "id_especie" in datos else 0
    puentes = datos["id_lugar"].nunique() if "id_lugar" in datos else 0
    presentes = len(datos[datos["presencia"] == "PRESENTE"]) if "presencia" in datos else 0
    rejilla_metricas(
        [
            ("Detecciones", str(len(datos)) if len(datos) else "Sin datos", "Registros filtrados"),
            ("Especies", str(especies) if especies else "Sin datos", "Especies detectadas"),
            ("Puentes", str(puentes) if puentes else "Sin datos", "Puentes con datos"),
            ("Presentes", str(presentes) if presentes else "Sin datos", "Registros PRESENTE"),
        ]
    )


def _render_graficos(datos: pd.DataFrame) -> None:
    """Gráficos de mamíferos."""
    col1, col2 = st.columns(2)
    with col1:
        _grafico(_conteo(datos, "tipo_evidencia"), "tipo_evidencia", "total", "Evidencias")
        _grafico(_diversidad_por_puente(datos), "nombre_lugar", "especies", "Ranking de puentes por diversidad")
    with col2:
        _grafico(_conteo(datos, "presencia"), "presencia", "total", "Resumen por presencia")
        _grafico(_especies_por_puente(datos), "nombre_lugar", "registros", "Especies por puente")


def _render_mapa(datos: pd.DataFrame) -> None:
    """Mapa de puentes por especie filtrada."""
    st.subheader("Mapa de puentes")
    lugares = datos.drop_duplicates("id_lugar") if "id_lugar" in datos else pd.DataFrame()
    if lugares.empty:
        st.info("Sin coordenadas de puentes para los filtros.")
        return
    st_folium(mapa_lugares(lugares, "Mamíferos puentes"), use_container_width=True, height=460)


def _render_tabla_y_detalle(datos: pd.DataFrame, tablas: dict[str, pd.DataFrame]) -> None:
    """Tabla y detalle de detecciones."""
    st.subheader("Detecciones")
    columnas = ["id_mamifero", "fecha", "nombre_lugar", "nombre_comun", "presencia", "tipo_evidencia", "observaciones"]
    tabla_datos(datos[[c for c in columnas if c in datos]], "Sin detecciones para los filtros.")
    if datos.empty:
        return
    seleccion = st.selectbox(
        "Detalle de detección",
        datos.index,
        format_func=lambda idx: etiqueta_registro(datos.loc[idx], "id_mamifero", ["fecha", "nombre_lugar", "nombre_comun", "tipo_evidencia"]),
    )
    registro = datos.loc[seleccion]
    with st.container(border=True):
        st.subheader("Detalle")
        st.write(registro[[c for c in columnas if c in registro.index]].to_dict())
        st.caption("Fotos asociadas")
        fotos = filtrar_fotos_asociadas(tablas.get("fotos", pd.DataFrame()), registro.get("id_visita"), "mamiferos_puentes", registro.get("id_mamifero"))
        mostrar_enlaces_fotos(enlaces_drive(fotos))


def _grafico(df: pd.DataFrame, x: str, y: str, titulo: str) -> None:
    """Muestra gráfico o aviso."""
    chart = None if df.empty else grafico_barras(df, x, y)
    bloque_grafico(titulo, chart)


def _conteo(datos: pd.DataFrame, columna: str) -> pd.DataFrame:
    """Cuenta por columna."""
    if datos.empty or columna not in datos:
        return pd.DataFrame(columns=[columna, "total"])
    return datos.groupby(columna, dropna=False).size().reset_index(name="total")


def _diversidad_por_puente(datos: pd.DataFrame) -> pd.DataFrame:
    """Cuenta especies por puente."""
    if datos.empty or not {"nombre_lugar", "id_especie"}.issubset(datos.columns):
        return pd.DataFrame(columns=["nombre_lugar", "especies"])
    return datos.groupby("nombre_lugar")["id_especie"].nunique().reset_index(name="especies").sort_values("especies", ascending=False)


def _especies_por_puente(datos: pd.DataFrame) -> pd.DataFrame:
    """Cuenta registros por puente."""
    if datos.empty or "nombre_lugar" not in datos:
        return pd.DataFrame(columns=["nombre_lugar", "registros"])
    return datos.groupby("nombre_lugar").size().reset_index(name="registros")


def _rango_fechas(columna, datos: pd.DataFrame):
    """Selector de fechas."""
    fechas = pd.to_datetime(datos["fecha"], errors="coerce").dropna().dt.date
    if fechas.empty:
        return None, None
    rango = columna.date_input("Fecha", value=(fechas.min(), fechas.max()), key="mamiferos_fecha")
    return rango if isinstance(rango, tuple) and len(rango) == 2 else (None, None)
