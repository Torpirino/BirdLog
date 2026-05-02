"""Página de consulta de nidos de rapaces."""

import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from dashboard.lib.consultas import cargar_tablas_consulta, etiqueta_registro, observaciones_legibles
from dashboard.lib.filtros import filtrar_fecha, filtrar_lugar, filtrar_valores, opciones_unicas
from dashboard.lib.fotos import enlaces_drive, filtrar_fotos_asociadas
from dashboard.lib.mapas import mapa_lugares
from dashboard.lib.ui import encabezado_pagina, mostrar_enlaces_fotos, rejilla_metricas, tabla_datos


@st.cache_data(ttl=120)
def _cargar_datos() -> dict[str, pd.DataFrame]:
    """Carga datos de nidos rapaces."""
    return cargar_tablas_consulta()


def render() -> None:
    """Renderiza la página de nidos rapaces."""
    encabezado_pagina(
        "Nidos rapaces",
        "Histórico de revisiones, localización real, texto de campo y fotos.",
        "🪶",
    )
    try:
        tablas = _cargar_datos()
    except Exception as exc:
        st.warning(f"No se pudieron cargar datos: {exc}")
        return
    datos = observaciones_legibles("nidos_rapaces", tablas)
    if datos.empty:
        st.info("Sin datos de nidos rapaces todavía.")
        return
    filtrados = _render_filtros(datos)
    _render_resumen(filtrados)
    _render_mapa(filtrados)
    _render_historico(filtrados, tablas)


def _render_filtros(datos: pd.DataFrame) -> pd.DataFrame:
    """Dibuja filtros de rapaces."""
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        desde, hasta = _rango_fechas(c1, datos)
        especies = c2.multiselect("Especie", opciones_unicas(datos, "nombre_comun"))
        lugares = c3.multiselect("Lugar / nido", opciones_unicas(datos, "nombre_lugar"))
    filtrados = filtrar_fecha(datos, desde=desde, hasta=hasta)
    filtrados = filtrar_valores(filtrados, "nombre_comun", especies)
    return filtrar_lugar(filtrados, lugares)


def _render_resumen(datos: pd.DataFrame) -> None:
    """Muestra métricas de rapaces."""
    nidos = datos["id_lugar"].nunique() if "id_lugar" in datos else 0
    especies = datos["id_especie"].nunique() if "id_especie" in datos else 0
    ultima = _ultima_fecha(datos)
    rejilla_metricas(
        [
            ("Revisiones", str(len(datos)) if len(datos) else "Sin datos", "Registros filtrados"),
            ("Nidos", str(nidos) if nidos else "Sin datos", "Lugares únicos"),
            ("Especies", str(especies) if especies else "Sin datos", "Especies revisadas"),
            ("Última revisión", ultima, "Fecha más reciente"),
        ]
    )


def _render_mapa(datos: pd.DataFrame) -> None:
    """Muestra mapa de nidos."""
    st.subheader("Mapa de nidos")
    lugares = datos.drop_duplicates("id_lugar") if "id_lugar" in datos else pd.DataFrame()
    if lugares.empty:
        st.info("Sin coordenadas de nidos para los filtros.")
        return
    st_folium(mapa_lugares(lugares, "Nidos rapaces"), use_container_width=True, height=460)
    columnas = ["nombre_lugar", "municipio", "utm_x", "utm_y"]
    tabla_datos(lugares[[c for c in columnas if c in lugares]], "Sin coordenadas para mostrar.")


def _render_historico(datos: pd.DataFrame, tablas: dict[str, pd.DataFrame]) -> None:
    """Tabla y ficha detallada."""
    st.subheader("Revisiones")
    columnas = ["id_nido_rapaz", "fecha", "nombre_lugar", "nombre_comun", "comunicacion_personal"]
    tabla_datos(datos[[c for c in columnas if c in datos]], "Sin revisiones para los filtros.")
    if datos.empty:
        return
    seleccion = st.selectbox(
        "Ficha de revisión",
        datos.index,
        format_func=lambda idx: etiqueta_registro(datos.loc[idx], "id_nido_rapaz", ["fecha", "nombre_lugar", "nombre_comun"]),
    )
    _render_ficha(datos.loc[seleccion], tablas)


def _render_ficha(registro: pd.Series, tablas: dict[str, pd.DataFrame]) -> None:
    """Ficha detallada de revisión."""
    with st.container(border=True):
        st.subheader(registro.get("nombre_lugar") or "Nido")
        st.caption(f"{registro.get('fecha', '')} · {registro.get('nombre_comun', 'Especie sin indicar')}")
        st.write("Texto de revisión")
        st.info(str(registro.get("texto_revision") or "Sin texto de revisión."))
        st.write("Comunicación personal")
        st.caption(str(registro.get("comunicacion_personal") or "Sin comunicación personal."))
        st.write({"utm_x": registro.get("utm_x"), "utm_y": registro.get("utm_y")})
        st.caption("Fotos asociadas")
        fotos = filtrar_fotos_asociadas(tablas.get("fotos", pd.DataFrame()), registro.get("id_visita"), "nidos_rapaces", registro.get("id_nido_rapaz"))
        mostrar_enlaces_fotos(enlaces_drive(fotos))


def _rango_fechas(columna, datos: pd.DataFrame):
    """Selector de fechas."""
    fechas = pd.to_datetime(datos["fecha"], errors="coerce").dropna().dt.date
    if fechas.empty:
        return None, None
    rango = columna.date_input("Fecha", value=(fechas.min(), fechas.max()), key="rapaces_fecha")
    return rango if isinstance(rango, tuple) and len(rango) == 2 else (None, None)


def _ultima_fecha(datos: pd.DataFrame) -> str:
    """Última fecha legible."""
    if datos.empty or "fecha" not in datos:
        return "Sin datos"
    fecha = pd.to_datetime(datos["fecha"], errors="coerce").max()
    return "Sin datos" if pd.isna(fecha) else fecha.strftime("%d/%m/%Y")
