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
from dashboard.lib.graficos import (
    COLOR_NARANJA,
    COLOR_VERDE,
    grafico_barras,
    grafico_lineas,
    visitas_por_mes,
)
from dashboard.lib.ui import bloque_grafico, separador_seccion, tabla_datos


METRICAS_PRINCIPALES = [
    "Total visitas",
    "Especies observadas",
    "Observaciones Lindus",
    "Capturas vv",
]
ICONOS_METRICAS = {
    "Total visitas": "📍",
    "Especies observadas": "🌿",
    "Observaciones Lindus": "🦅",
    "Capturas vv": "🪤",
    "Última visita": "📅",
    "Lugares activos": "🗺️",
    "Cajas ocupadas": "🏡",
    "Mamíferos detectados": "🐾",
}
ETIQUETAS_METRICAS = {
    "Capturas vv": "Capturas VV",
}
TIPOS_VISITA = {
    "LINDUS": "Lindus",
    "CAJA_NIDO": "Cajas nido",
    "CEBO_AVISPON": "Cebos avispones",
    "NIDO_RAPAZ": "Nidos rapaces",
    "MAMIFEROS_PUENTES": "Mamíferos puentes",
    "Lindus": "Lindus",
    "Caja nido": "Cajas nido",
    "Cebo avispón": "Cebos avispones",
    "Nido rapaz": "Nidos rapaces",
    "Mamífero puente": "Mamíferos puentes",
}


@st.cache_data(ttl=120)
def _cargar_datos() -> dict[str, pd.DataFrame]:
    """Carga datos de portada con caché corta."""
    return cargar_tablas_dashboard()


def render() -> None:
    """Renderiza la página de resumen inicial."""
    st.title("Inicio")
    try:
        tablas = _cargar_datos()
    except Exception as exc:
        st.warning(f"No se pudieron cargar datos: {exc}")
        return

    st.subheader("Resumen general")
    _render_metricas(metricas_inicio(tablas))
    _render_graficos(tablas)
    _render_ultimos_registros(tablas)


def _render_metricas(metricas: list[tuple[str, str, str]]) -> None:
    """Muestra métricas principales y secundarias en bloques compactos."""
    por_titulo = {titulo: (valor, ayuda) for titulo, valor, ayuda in metricas}
    principales = [
        (titulo, *por_titulo[titulo])
        for titulo in METRICAS_PRINCIPALES
        if titulo in por_titulo
    ]
    secundarias = [
        (titulo, valor, ayuda)
        for titulo, valor, ayuda in metricas
        if titulo not in METRICAS_PRINCIPALES
    ]

    _fila_metricas(principales, columnas=4)
    if secundarias:
        st.caption("Indicadores secundarios")
        _fila_metricas(secundarias, columnas=4)


def _fila_metricas(metricas: list[tuple[str, str, str]], columnas: int) -> None:
    """Dibuja una fila de métricas en contenedores nativos."""
    for columna, (titulo, valor, ayuda) in zip(st.columns(columnas), metricas, strict=False):
        with columna.container(border=True):
            etiqueta = ETIQUETAS_METRICAS.get(titulo, titulo)
            etiqueta = f"{ICONOS_METRICAS.get(titulo, '')} {etiqueta}".strip()
            st.metric(etiqueta, valor, help=ayuda)


def _render_graficos(tablas: dict[str, pd.DataFrame]) -> None:
    """Dibuja gráficos principales."""
    visitas = visitas_legibles(tablas)
    st.subheader("Actividad reciente")
    col_izq, col_der = st.columns(2)
    with col_izq:
        _chart_o_vacio(visitas_por_mes(visitas), "mes", "visitas", "Visitas por mes", "lineas")
        bloque_grafico("Especies más registradas", _grafico_especies(ranking_especies(tablas, limite=10)))
    with col_der:
        _chart_o_vacio(_visitas_por_tipo(visitas), "Tipo", "Visitas", "Visitas por tipo")
        bloque_grafico("Evolución de capturas VV", _grafico_capturas_vv(_capturas_vv_por_fecha(tablas)))


def _render_ultimos_registros(tablas: dict[str, pd.DataFrame]) -> None:
    """Muestra tabla de últimos registros."""
    separador_seccion("Últimos registros")
    tabla_datos(_tabla_ultimos_registros(tablas), "Sin registros recientes.")


def _chart_o_vacio(df: pd.DataFrame, x: str, y: str, titulo: str, tipo: str = "barras") -> None:
    """Muestra gráfico o mensaje sin datos."""
    chart = None
    if not df.empty:
        chart = grafico_lineas(df, x, y, titulo="") if tipo == "lineas" else grafico_barras(df, x, y, titulo="")
    bloque_grafico(titulo, chart)


def _grafico_especies(df: pd.DataFrame) -> alt.Chart | None:
    """Crea ranking horizontal de especies."""
    if df.empty:
        return None
    datos = df.copy().head(10)
    datos["Especie"] = datos.get("especie", datos["id_especie"]).map(_limpiar_texto)
    datos["Registros"] = pd.to_numeric(datos["registros"], errors="coerce").fillna(0)
    return alt.Chart(datos).mark_bar(color=COLOR_VERDE).encode(
        x=alt.X("Registros:Q", title="Registros"),
        y=alt.Y("Especie:N", sort="-x", title="Especie"),
        tooltip=["Especie", "Registros"],
    ).properties(height=280)


def _grafico_capturas_vv(df: pd.DataFrame) -> alt.Chart | None:
    """Crea gráfico temporal legible de capturas VV."""
    if df.empty:
        return None
    datos = df.copy()
    datos["fecha_dt"] = pd.to_datetime(datos["fecha"], errors="coerce")
    datos = datos.dropna(subset=["fecha_dt"]).sort_values("fecha_dt")
    if datos.empty:
        return None
    datos["Fecha"] = datos["fecha_dt"].map(_formatear_fecha_corta)
    datos["Capturas VV"] = pd.to_numeric(datos["vv"], errors="coerce").fillna(0)
    return alt.Chart(datos).mark_bar(color=COLOR_NARANJA).encode(
        x=alt.X("Fecha:N", sort=list(datos["Fecha"]), title="Fecha"),
        y=alt.Y("Capturas VV:Q", title="Capturas VV"),
        tooltip=["Fecha", "Capturas VV"],
    ).properties(height=280)


def _visitas_por_tipo(visitas: pd.DataFrame) -> pd.DataFrame:
    """Cuenta visitas usando etiquetas legibles."""
    datos = conteo_por(visitas, "tipo_visita", "Visitas")
    if datos.empty:
        return pd.DataFrame(columns=["Tipo", "Visitas"])
    datos["Tipo"] = datos["tipo_visita"].map(_formatear_tipo)
    return datos[["Tipo", "Visitas"]]


def _capturas_vv_por_fecha(tablas: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Calcula capturas vv por fecha de visita."""
    cebos = tablas.get("cebos_avispones", pd.DataFrame())
    visitas = visitas_legibles(tablas)
    if cebos.empty or "vv" not in cebos or visitas.empty:
        return pd.DataFrame(columns=["fecha", "vv"])
    datos = cebos.merge(visitas[["id_visita", "fecha"]], on="id_visita", how="left")
    datos["vv"] = pd.to_numeric(datos["vv"], errors="coerce").fillna(0)
    return datos.groupby("fecha", dropna=False)["vv"].sum().reset_index()


def _tabla_ultimos_registros(tablas: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Prepara últimos registros con columnas pensadas para lectura."""
    datos = ultimos_registros(tablas, limite=10)
    if datos.empty:
        return pd.DataFrame(columns=["Fecha", "Tipo", "Lugar", "Especie", "Observaciones"])
    tabla = pd.DataFrame(
        {
            "Fecha": pd.to_datetime(datos.get("fecha"), errors="coerce").dt.strftime("%d/%m/%Y"),
            "Tipo": datos.get("tipo", pd.Series(dtype=str)).map(_formatear_tipo),
            "Lugar": _elegir_lugar(datos),
            "Especie": datos.get("especie", pd.Series(dtype=str)).map(_limpiar_texto),
            "Observaciones": datos.get("observaciones", pd.Series(dtype=str)).map(_limpiar_texto),
        }
    )
    return tabla.fillna("").replace("", "—")


def _elegir_lugar(datos: pd.DataFrame) -> pd.Series:
    """Elige una única columna de lugar clara."""
    lugar = datos.get("nombre_lugar", pd.Series("", index=datos.index)).copy()
    lugar_visita = datos.get("nombre_lugar_visita", pd.Series("", index=datos.index))
    lugar = lugar.where(lugar.notna() & (lugar.astype(str).str.strip() != ""), lugar_visita)
    return lugar.map(_limpiar_texto)


def _limpiar_texto(valor: object) -> str:
    """Oculta ruido técnico y normaliza vacíos para la interfaz."""
    if pd.isna(valor):
        return ""
    texto = str(valor).replace("[SINTETICO_TEST]", "").strip()
    if texto.lower() in {"none", "nan", "nat"}:
        return ""
    return " ".join(texto.split())


def _formatear_tipo(valor: object) -> str:
    """Convierte tipos técnicos o internos en etiquetas humanas."""
    texto = _limpiar_texto(valor)
    return TIPOS_VISITA.get(texto, texto.replace("_", " ").title())


def _formatear_fecha_corta(fecha: pd.Timestamp) -> str:
    """Formatea fecha como día y mes abreviado en español."""
    meses = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
    return f"{fecha.day:02d} {meses[fecha.month - 1]}"
