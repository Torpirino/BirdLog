"""Componentes visuales reutilizables del dashboard."""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd
import streamlit as st

from dashboard.lib.conexion import EstadoConexion


ICONOS = {
    "Inicio": "🏠",
    "Mapa general": "🗺️",
    "Lindus": "🦅",
    "Cajas nido": "🏡",
    "Nidos rapaces": "🪶",
    "Cebos avispones": "🪤",
    "Mamíferos puentes": "🐾",
    "Edición / Catálogos": "✏️",
}

def aplicar_estilos() -> None:
    """Mantiene el punto de entrada visual común del dashboard."""
    return None


def render_sidebar(paginas: Iterable[str]) -> str:
    """Dibuja el menú lateral y devuelve la página activa."""
    opciones = list(paginas)
    if not opciones:
        raise ValueError("El dashboard necesita al menos una página.")
    pagina_actual = st.session_state.get("pagina_activa")
    if pagina_actual not in opciones:
        st.session_state["pagina_activa"] = opciones[0]

    with st.sidebar:
        st.markdown("## BirdLog")
        st.caption("Datos de fauna")
        for pagina in opciones:
            activa = pagina == st.session_state["pagina_activa"]
            if st.button(
                f"{ICONOS.get(pagina, '•')}  {pagina}",
                key=f"nav_{pagina}",
                type="primary" if activa else "secondary",
                use_container_width=True,
            ):
                st.session_state["pagina_activa"] = pagina
                st.rerun()
        return st.session_state["pagina_activa"]


def encabezado_pagina(titulo: str) -> None:
    """Muestra el título real de cada página."""
    if not titulo:
        raise ValueError("Cada página debe definir un título explícito.")
    st.title(titulo)


def panel_filtros():
    """Contenedor visible y compacto para filtros de página."""
    return st.container(border=True)


def separador_seccion(texto: str) -> None:
    """Dibuja un título de sección sobrio."""
    st.markdown(f"#### {texto}")


def sin_datos(mensaje: str = "Sin datos para los filtros seleccionados.") -> None:
    """Muestra un estado vacío con componentes nativos."""
    st.info(mensaje)


def bloque_grafico(titulo: str, chart=None) -> None:
    """Contenedor estándar para un gráfico Altair con gestión de vacío."""
    with st.container(border=True):
        st.markdown(f"#### {titulo}")
        if chart is None:
            sin_datos()
        else:
            st.altair_chart(chart, use_container_width=True)


def tarjeta_metrica(titulo: str, valor: str, ayuda: str = "") -> None:
    """Dibuja una métrica con estilo de tarjeta."""
    st.metric(titulo, valor, help=ayuda or None)


def rejilla_metricas(metricas: list[tuple[str, str, str]]) -> None:
    """Dibuja métricas en columnas equilibradas."""
    columnas = st.columns(len(metricas) or 1)
    for columna, (titulo, valor, ayuda) in zip(columnas, metricas, strict=False):
        with columna:
            tarjeta_metrica(titulo, valor, ayuda)


def panel(titulo: str, texto: str | None = None):
    """Crea un contenedor con borde y título."""
    contenedor = st.container(border=True)
    contenedor.subheader(titulo)
    if texto:
        contenedor.caption(texto)
    return contenedor


def bloque_placeholder(titulo: str, texto: str) -> None:
    """Muestra un bloque elegante para páginas aún no implementadas."""
    with st.container(border=True):
        st.subheader(titulo)
        st.caption(texto)


def bloque_info(texto: str) -> None:
    """Muestra una nota informativa contenida."""
    st.info(texto)


def tabla_datos(df: pd.DataFrame, mensaje_vacio: str = "Sin datos para los filtros seleccionados.") -> None:
    """Muestra una tabla o un bloque vacío estilizado si no hay datos."""
    if df.empty:
        sin_datos(mensaje_vacio)
        return
    st.dataframe(df, hide_index=True, use_container_width=True)


def mostrar_enlaces_fotos(enlaces: list[dict[str, str]]) -> None:
    """Muestra enlaces de fotos como botones distribuidos en columnas."""
    if not enlaces:
        st.caption("📷 Sin fotos asociadas.")
        return
    columnas = st.columns(min(len(enlaces), 4))
    for col, enlace in zip(columnas, enlaces):
        col.link_button(
            f"📷 {enlace.get('descripcion', 'Ver foto')}",
            enlace["url"],
            use_container_width=True,
        )


def aviso_estado(tipo: str, mensaje: str) -> None:
    """Muestra un aviso de estado homogéneo."""
    {"ok": st.success, "info": st.info, "warning": st.warning, "error": st.error}.get(
        tipo, st.info
    )(mensaje)


def estado_conexion(estado: EstadoConexion) -> None:
    """Muestra el estado de conexión en la barra lateral."""
    with st.sidebar:
        st.divider()
        st.caption(f"Entorno: {estado.entorno}")
        if estado.ok:
            st.success(estado.mensaje)
        else:
            st.warning(estado.mensaje)
