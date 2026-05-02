"""Componentes visuales reutilizables del dashboard."""

from collections.abc import Iterable

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
        .birdlog-eyebrow {
            color: #56745d;
            font-size: 0.82rem;
            font-weight: 700;
            letter-spacing: 0;
            text-transform: uppercase;
        }
        .birdlog-title {
            color: #173b27;
            font-size: 2rem;
            font-weight: 800;
            margin: 0.1rem 0 0.25rem;
        }
        .birdlog-subtitle {
            color: #52685a;
            font-size: 1rem;
            margin: 0 0 1.2rem;
        }
        .birdlog-placeholder {
            min-height: 16rem;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            color: #496250;
            background:
                linear-gradient(135deg, rgba(234, 242, 226, 0.95), rgba(255, 255, 250, 0.95));
            border: 1px dashed #b8c8ad;
            border-radius: 16px;
            padding: 2rem;
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
    st.markdown(
        f"""
        <div>
            <div class="birdlog-eyebrow">{icono} BirdLog</div>
            <h1 class="birdlog-title">{titulo}</h1>
            <p class="birdlog-subtitle">{subtitulo}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def tarjeta_metrica(titulo: str, valor: str, ayuda: str = "") -> None:
    """Dibuja una métrica con estilo de tarjeta."""
    st.metric(titulo, valor, help=ayuda or None)


def bloque_placeholder(titulo: str, texto: str) -> None:
    """Muestra un bloque elegante para páginas aún no implementadas."""
    st.markdown(
        f"""
        <div class="birdlog-placeholder">
            <div>
                <h3>{titulo}</h3>
                <p>{texto}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def bloque_info(texto: str) -> None:
    """Muestra una nota informativa contenida."""
    st.info(texto)


def estado_conexion(estado: EstadoConexion) -> None:
    """Muestra el estado de conexión en la barra lateral."""
    with st.sidebar:
        st.divider()
        st.caption(f"Entorno: {estado.entorno}")
        if estado.ok:
            st.success(estado.mensaje)
        else:
            st.warning(estado.mensaje)
