"""Componentes visuales reutilizables del dashboard."""

from collections.abc import Iterable

import pandas as pd
import streamlit as st

from dashboard.lib.conexion import EstadoConexion


ICONOS = {
    "Inicio / Resumen": "🏠",
    "Mapa general": "🗺️",
    "Lindus": "🦅",
    "Cajas nido": "🏡",
    "Nidos rapaces": "🪶",
    "Cebos avispones": "🪤",
    "Mamíferos puentes": "🐾",
    "Edición / Catálogos": "✏️",
}


def aplicar_estilos() -> None:
    """Aplica una capa visual común sobre el tema Streamlit."""
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(210, 230, 196, 0.55), transparent 34rem),
                #f7f8f1;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #123f28 0%, #1e5d39 100%);
        }
        [data-testid="stSidebar"] * {
            color: #f7fbf3;
        }
        [data-testid="stSidebar"] .stRadio label {
            padding: 0.28rem 0;
        }
        div[data-testid="stMetric"],
        .birdlog-card {
            background: rgba(255, 255, 250, 0.92);
            border: 1px solid #d9e2d1;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(33, 72, 45, 0.08);
            padding: 1rem 1.1rem;
        }
        .stButton > button {
            border-radius: 10px;
            border-color: #b7c8ae;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(paginas: Iterable[str]) -> str:
    """Dibuja el menú lateral y devuelve la página activa."""
    opciones = list(paginas)
    with st.sidebar:
        st.markdown("## 🌿 BirdLog")
        st.caption("Conservación y monitoreo local")
        etiquetas = [f"{ICONOS.get(pagina, '•')}  {pagina}" for pagina in opciones]
        seleccion = st.radio("Navegación", etiquetas, label_visibility="collapsed")
    indice = etiquetas.index(seleccion)
    return opciones[indice]


def encabezado_pagina(titulo: str, subtitulo: str, icono: str = "🌿") -> None:
    """Muestra un encabezado visual homogéneo."""
    st.caption(f"{icono} BirdLog")
    st.title(titulo)
    st.write(subtitulo)


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


def tabla_datos(df: pd.DataFrame, mensaje_vacio: str = "No hay datos para mostrar.") -> None:
    """Muestra una tabla clara o un aviso si está vacía."""
    if df.empty:
        st.info(mensaje_vacio)
        return
    st.dataframe(df, use_container_width=True, hide_index=True)


def mostrar_enlaces_fotos(enlaces: list[dict[str, str]]) -> None:
    """Muestra enlaces de fotos de Drive sin embeber credenciales."""
    if not enlaces:
        st.caption("Sin fotos asociadas.")
        return
    for enlace in enlaces:
        st.link_button(enlace["descripcion"], enlace["url"])


def aviso_estado(tipo: str, mensaje: str) -> None:
    """Muestra un aviso de estado homogéneo."""
    avisos = {
        "ok": st.success,
        "info": st.info,
        "warning": st.warning,
        "error": st.error,
    }
    avisos.get(tipo, st.info)(mensaje)


def estado_conexion(estado: EstadoConexion) -> None:
    """Muestra el estado de conexión en la barra lateral."""
    with st.sidebar:
        st.divider()
        st.caption(f"Entorno: {estado.entorno}")
        if estado.ok:
            st.success(estado.mensaje)
        else:
            st.warning(estado.mensaje)
