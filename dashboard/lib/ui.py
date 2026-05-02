"""Componentes visuales reutilizables del dashboard."""

from __future__ import annotations

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

_CSS = """
<style>
/* ── Fondo ────────────────────────────────────────────────────────── */
.stApp {
    background:
        radial-gradient(circle at top left, rgba(210,230,196,.45), transparent 30rem),
        #f5f7f0;
}

/* ── Barra lateral ───────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0c2f1e 0%, #163d28 50%, #1a5230 100%);
}
[data-testid="stSidebar"] * { color: #dff0dc; }
[data-testid="stSidebar"] .stRadio label {
    padding: .32rem 0; font-size: .9rem; transition: color .15s;
}
[data-testid="stSidebar"] .stRadio label:hover { color: #a8e6c1; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.1); }

/* ── Logo sidebar ────────────────────────────────────────────────── */
.bl-logo {
    font-size: 1.2rem; font-weight: 700;
    color: #c8f0c8; letter-spacing: .05em;
    padding: .5rem 0 0;
}
.bl-logo-sub {
    font-size: .7rem; color: #7dab90;
    margin-bottom: .6rem; letter-spacing: .03em;
}

/* ── Cabecera de página ──────────────────────────────────────────── */
.bl-header {
    display: flex; align-items: center; gap: 1rem;
    background: linear-gradient(105deg, #1a5230 0%, #2f6f3e 55%, #3d8a50 100%);
    border-radius: 14px; padding: .95rem 1.4rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 4px 18px rgba(22,61,40,.2);
}
.bl-header-icon { font-size: 2rem; flex-shrink: 0; line-height: 1; }
.bl-header-title {
    font-size: 1.5rem; font-weight: 700;
    color: #f0faf0; letter-spacing: -.01em; line-height: 1.2;
}
.bl-header-sub {
    font-size: .85rem; color: rgba(240,250,240,.72); margin-top: .18rem;
}

/* ── Tarjetas de métrica ─────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: white;
    border: 1px solid #d8e8cf;
    border-left: 4px solid #2f6f3e;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(30,70,45,.07);
    padding: .9rem 1.1rem !important;
    transition: box-shadow .2s;
}
[data-testid="stMetric"]:hover {
    box-shadow: 0 4px 18px rgba(30,70,45,.13);
}
[data-testid="stMetricValue"] {
    font-size: 2rem !important; font-weight: 700 !important;
    color: #173b27 !important;
}
[data-testid="stMetricLabel"] {
    font-size: .72rem !important; font-weight: 600 !important;
    text-transform: uppercase; letter-spacing: .06em;
    color: #5a7a65 !important;
}

/* ── Contenedores bordeados (filtros, gráficos, detalle) ─────────── */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 13px !important;
    border: 1px solid #dce8d4 !important;
    background: rgba(255,255,254,.97) !important;
    box-shadow: 0 2px 10px rgba(30,70,45,.05) !important;
}

/* ── Separador de sección ────────────────────────────────────────── */
.bl-seccion {
    font-size: .68rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: .08em;
    color: #5a7a65; padding: .05rem 0 .45rem;
    border-bottom: 2px solid #e4edda; margin-bottom: .65rem;
}

/* ── Estado vacío ────────────────────────────────────────────────── */
.bl-empty {
    text-align: center; padding: 2.2rem 1.2rem;
    background: #f4faf1; border-radius: 12px;
    border: 1.5px dashed #b5c8ab;
}
.bl-empty-icon { font-size: 1.7rem; margin-bottom: .35rem; }
.bl-empty-msg { font-size: .88rem; color: #5a7a65; }

/* ── Botones ─────────────────────────────────────────────────────── */
.stButton > button {
    border-radius: 8px; border: 1.5px solid #2f6f3e;
    color: #2f6f3e; font-weight: 500;
    transition: background .18s, color .18s;
}
.stButton > button:hover { background: #2f6f3e !important; color: white !important; }

/* ── Enlace de fotos ─────────────────────────────────────────────── */
.stLinkButton > a {
    border-radius: 8px !important;
    border: 1.5px solid #2f6f3e !important;
    color: #2f6f3e !important; font-size: .83rem !important;
    font-weight: 500 !important; padding: .3rem .65rem !important;
}

/* ── Alertas ─────────────────────────────────────────────────────── */
[data-testid="stAlert"] { border-radius: 10px; }

/* ── Encabezados ─────────────────────────────────────────────────── */
h2, h3 { color: #173b27 !important; }

/* ── Tabla ───────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
</style>
"""


def aplicar_estilos() -> None:
    """Aplica la capa visual común sobre el tema Streamlit."""
    st.markdown(_CSS, unsafe_allow_html=True)


def render_sidebar(paginas: Iterable[str]) -> str:
    """Dibuja el menú lateral y devuelve la página activa."""
    opciones = list(paginas)
    with st.sidebar:
        st.markdown('<div class="bl-logo">🌿 BirdLog</div>', unsafe_allow_html=True)
        st.markdown('<div class="bl-logo-sub">Conservación y monitoreo local</div>', unsafe_allow_html=True)
        etiquetas = [f"{ICONOS.get(p, '•')}  {p}" for p in opciones]
        seleccion = st.radio("Navegación", etiquetas, label_visibility="collapsed")
    return opciones[etiquetas.index(seleccion)]


def encabezado_pagina(titulo: str, subtitulo: str, icono: str = "🌿") -> None:
    """Muestra un encabezado con banner verde homogéneo."""
    st.markdown(
        f"""
        <div class="bl-header">
            <span class="bl-header-icon">{icono}</span>
            <div>
                <div class="bl-header-title">{titulo}</div>
                <div class="bl-header-sub">{subtitulo}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def separador_seccion(texto: str) -> None:
    """Dibuja un separador de sección con etiqueta en mayúsculas."""
    st.markdown(f'<div class="bl-seccion">{texto}</div>', unsafe_allow_html=True)


def sin_datos(mensaje: str = "Sin datos para los filtros seleccionados.") -> None:
    """Muestra un bloque vacío estilizado."""
    st.markdown(
        f"""
        <div class="bl-empty">
            <div class="bl-empty-icon">🌿</div>
            <div class="bl-empty-msg">{mensaje}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def bloque_grafico(titulo: str, chart=None) -> None:
    """Contenedor estándar para un gráfico Altair con gestión de vacío."""
    with st.container(border=True):
        separador_seccion(titulo)
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
