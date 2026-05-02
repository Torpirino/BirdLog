"""Página de consulta Lindus."""

from datetime import time

import pandas as pd
import streamlit as st

from dashboard.lib.consultas import (
    cargar_tablas_consulta,
    etiqueta_registro,
    meteorologia_de_visita,
    observaciones_legibles,
    sumar_por,
)
from dashboard.lib.filtros import filtrar_fecha, filtrar_lugar, filtrar_rango_numerico, filtrar_valores, opciones_unicas
from dashboard.lib.fotos import enlaces_drive, filtrar_fotos_asociadas
from dashboard.lib.graficos import acumulado, grafico_barras, grafico_lineas
from dashboard.lib.ui import encabezado_pagina, mostrar_enlaces_fotos, rejilla_metricas, tabla_datos


@st.cache_data(ttl=120)
def _cargar_datos() -> dict[str, pd.DataFrame]:
    """Carga datos de consulta Lindus."""
    return cargar_tablas_consulta()


def render() -> None:
    """Renderiza la página Lindus."""
    encabezado_pagina(
        "Lindus",
        "Consulta de observaciones migratorias, meteorología y fotos asociadas.",
        "🦅",
    )
    try:
        tablas = _cargar_datos()
    except Exception as exc:
        st.warning(f"No se pudieron cargar datos: {exc}")
        return
    datos = observaciones_legibles("lindus", tablas)
    if datos.empty:
        st.info("Sin observaciones Lindus todavía.")
        return
    filtrados = _render_filtros(datos)
    _render_metricas(filtrados)
    _render_graficos(filtrados)
    _render_tabla_y_detalle(filtrados, tablas)


def _render_filtros(datos: pd.DataFrame) -> pd.DataFrame:
    """Dibuja filtros Lindus."""
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        desde, hasta = _rango_fechas(c1, datos)
        especies = c2.multiselect("Especie", opciones_unicas(datos, "nombre_comun"))
        comportamientos = c3.multiselect("Comportamiento", opciones_unicas(datos, "comportamiento"))
        c4, c5, c6 = st.columns(3)
        observadores = c4.multiselect("Observador", opciones_unicas(datos, "nombre_observador"))
        lugares = c5.multiselect("Lugar", opciones_unicas(datos, "nombre_lugar_visita"))
        hora_min, hora_max = _rango_horas(c6, datos)
        n_min, n_max = _rango_numero(datos)
    filtrados = filtrar_fecha(datos, desde=desde, hasta=hasta)
    filtrados = filtrar_valores(filtrados, "nombre_comun", especies)
    filtrados = filtrar_valores(filtrados, "comportamiento", comportamientos)
    filtrados = filtrar_valores(filtrados, "nombre_observador", observadores)
    filtrados = filtrar_lugar(filtrados, lugares)
    filtrados = filtrar_rango_numerico(filtrados, "numero", n_min, n_max)
    return _filtrar_hora(filtrados, hora_min, hora_max)


def _render_metricas(datos: pd.DataFrame) -> None:
    """Muestra métricas Lindus."""
    individuos = int(pd.to_numeric(datos.get("numero", pd.Series(dtype=int)), errors="coerce").fillna(0).sum())
    especies = datos["id_especie"].nunique() if "id_especie" in datos else 0
    dias = datos["fecha"].nunique() if "fecha" in datos else 0
    rejilla_metricas(
        [
            ("Observaciones", str(len(datos)) if len(datos) else "Sin datos", "Registros filtrados"),
            ("Individuos", str(individuos) if individuos else "Sin datos", "Suma de individuos"),
            ("Especies", str(especies) if especies else "Sin datos", "Especies filtradas"),
            ("Días", str(dias) if dias else "Sin datos", "Días con registros"),
        ]
    )


def _render_graficos(datos: pd.DataFrame) -> None:
    """Dibuja gráficos Lindus."""
    col1, col2 = st.columns(2)
    with col1:
        _grafico(_por_dia(datos), "fecha", "individuos", "Individuos por día", "lineas")
        _grafico(sumar_por(datos, "nombre_comun", "numero", "individuos"), "nombre_comun", "individuos", "Individuos por especie")
        _grafico(acumulado(_por_dia(datos), "fecha", "individuos"), "fecha", "acumulado", "Acumulado por temporada", "lineas")
    with col2:
        _grafico(sumar_por(datos, "comportamiento", "numero", "individuos"), "comportamiento", "individuos", "MIGRADOR / NORTE / LOCAL")
        _grafico(sumar_por(datos, "hora", "numero", "individuos"), "hora", "individuos", "Paso por hora", "lineas")
        top = sumar_por(datos, "nombre_comun", "numero", "individuos").sort_values("individuos", ascending=False).head(10)
        _grafico(top, "nombre_comun", "individuos", "Top especies")


def _render_tabla_y_detalle(datos: pd.DataFrame, tablas: dict[str, pd.DataFrame]) -> None:
    """Muestra tabla y detalle de observación."""
    st.subheader("Observaciones")
    columnas = [
        "id_lindus",
        "fecha",
        "hora",
        "nombre_comun",
        "numero",
        "comportamiento",
        "nombre_lugar_visita",
        "nombre_observador",
    ]
    tabla_datos(datos[[c for c in columnas if c in datos.columns]], "Sin observaciones para los filtros.")
    if datos.empty:
        return
    seleccion = st.selectbox(
        "Detalle de observación",
        datos.index,
        format_func=lambda idx: etiqueta_registro(datos.loc[idx], "id_lindus", ["fecha", "hora", "nombre_comun", "numero"]),
    )
    _render_detalle(datos.loc[seleccion], tablas)


def _render_detalle(registro: pd.Series, tablas: dict[str, pd.DataFrame]) -> None:
    """Panel de detalle Lindus."""
    with st.container(border=True):
        st.subheader("Detalle")
        st.write(
            {
                "especie": registro.get("nombre_comun") or registro.get("nombre_cientifico"),
                "fecha": registro.get("fecha"),
                "hora": registro.get("hora"),
                "numero": registro.get("numero"),
                "comportamiento": registro.get("comportamiento"),
                "edad": registro.get("edad"),
                "sexo": registro.get("sexo"),
                "plumaje": registro.get("plumaje"),
                "observaciones": registro.get("observaciones"),
            }
        )
        st.caption("Meteorología asociada")
        tabla_datos(meteorologia_de_visita(tablas, registro.get("id_visita")), "Sin meteorología asociada.")
        st.caption("Fotos asociadas")
        fotos = tablas.get("fotos", pd.DataFrame())
        fotos = filtrar_fotos_asociadas(fotos, registro.get("id_visita"), "lindus", registro.get("id_lindus"))
        mostrar_enlaces_fotos(enlaces_drive(fotos))


def _grafico(df: pd.DataFrame, x: str, y: str, titulo: str, tipo: str = "barras") -> None:
    """Muestra gráfico o aviso sin datos."""
    with st.container(border=True):
        st.subheader(titulo)
        if df.empty:
            st.caption("Sin datos")
            return
        chart = grafico_lineas(df, x, y) if tipo == "lineas" else grafico_barras(df, x, y)
        st.altair_chart(chart, use_container_width=True)


def _por_dia(datos: pd.DataFrame) -> pd.DataFrame:
    """Suma individuos por día."""
    if datos.empty or not {"fecha", "numero"}.issubset(datos.columns):
        return pd.DataFrame(columns=["fecha", "individuos"])
    return datos.groupby("fecha")["numero"].sum().reset_index(name="individuos")


def _rango_fechas(columna, datos: pd.DataFrame):
    """Selector de fechas."""
    fechas = pd.to_datetime(datos["fecha"], errors="coerce").dropna().dt.date
    if fechas.empty:
        return None, None
    rango = columna.date_input("Fecha", value=(fechas.min(), fechas.max()), key="lindus_fecha")
    return rango if isinstance(rango, tuple) and len(rango) == 2 else (None, None)


def _rango_horas(columna, datos: pd.DataFrame) -> tuple[time | None, time | None]:
    """Selector de hora."""
    horas = pd.to_datetime(datos["hora"], errors="coerce").dropna().dt.time
    if horas.empty:
        return None, None
    hora_min, hora_max = min(horas), max(horas)
    if hora_min == hora_max:
        columna.caption(f"Hora: {hora_min}")
        return hora_min, hora_max
    return columna.slider("Hora", min_value=hora_min, max_value=hora_max, value=(hora_min, hora_max))


def _rango_numero(datos: pd.DataFrame) -> tuple[int, int]:
    """Selector de rango de número robusto."""
    numeros = pd.to_numeric(datos["numero"], errors="coerce").dropna()
    minimo, maximo = int(numeros.min()), int(numeros.max())
    if minimo == maximo:
        st.caption(f"Número de individuos: {minimo}")
        return minimo, maximo
    return st.slider("Número de individuos", min_value=minimo, max_value=maximo, value=(minimo, maximo))


def _filtrar_hora(datos: pd.DataFrame, hora_min: time | None, hora_max: time | None) -> pd.DataFrame:
    """Filtra por hora."""
    if datos.empty or "hora" not in datos or hora_min is None or hora_max is None:
        return datos
    horas = pd.to_datetime(datos["hora"], errors="coerce").dt.time
    return datos[(horas >= hora_min) & (horas <= hora_max)]
