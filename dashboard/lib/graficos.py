"""Gráficos Altair reutilizables."""

import altair as alt
import pandas as pd


COLOR_VERDE = "#2f6f3e"
COLOR_NARANJA = "#d98b2b"


def grafico_barras(
    df: pd.DataFrame, x: str, y: str, titulo: str = "", color: str = COLOR_VERDE
) -> alt.Chart:
    """Crea un gráfico de barras sencillo."""
    base = _base(df, titulo)
    return base.mark_bar(color=color, cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        x=alt.X(x, sort="-y"),
        y=alt.Y(y),
        tooltip=list(df.columns),
    )


def grafico_lineas(
    df: pd.DataFrame, x: str, y: str, titulo: str = "", color: str = COLOR_VERDE
) -> alt.Chart:
    """Crea un gráfico temporal de líneas con puntos."""
    base = _base(df, titulo)
    return base.mark_line(point=True, color=color).encode(
        x=alt.X(x),
        y=alt.Y(y),
        tooltip=list(df.columns),
    )


def grafico_area(df: pd.DataFrame, x: str, y: str, titulo: str = "") -> alt.Chart:
    """Crea un gráfico de área para acumulados."""
    return _base(df, titulo).mark_area(color=COLOR_VERDE, opacity=0.35).encode(
        x=alt.X(x),
        y=alt.Y(y),
        tooltip=list(df.columns),
    )


def grafico_donut(df: pd.DataFrame, categoria: str, valor: str, titulo: str = "") -> alt.Chart:
    """Crea un gráfico de anillo para composiciones."""
    return _base(df, titulo).mark_arc(innerRadius=55).encode(
        theta=alt.Theta(valor),
        color=alt.Color(categoria, scale=alt.Scale(scheme="greens")),
        tooltip=[categoria, valor],
    )


def visitas_por_mes(visitas: pd.DataFrame) -> pd.DataFrame:
    """Agrupa visitas por mes."""
    if visitas.empty or "fecha" not in visitas.columns:
        return pd.DataFrame(columns=["mes", "visitas"])
    df = visitas.copy()
    df["mes"] = pd.to_datetime(df["fecha"], errors="coerce").dt.to_period("M").astype(str)
    return df.groupby("mes").size().reset_index(name="visitas")


def acumulado(df: pd.DataFrame, ordenar_por: str, columna: str, salida: str = "acumulado") -> pd.DataFrame:
    """Calcula acumulado ordenado por una columna."""
    if df.empty or not {ordenar_por, columna}.issubset(df.columns):
        return pd.DataFrame(columns=[ordenar_por, salida])
    datos = df.sort_values(ordenar_por).copy()
    datos[salida] = pd.to_numeric(datos[columna], errors="coerce").fillna(0).cumsum()
    return datos[[ordenar_por, salida]]


def _base(df: pd.DataFrame, titulo: str) -> alt.Chart:
    """Base común para gráficos."""
    return alt.Chart(df, title=titulo).properties(height=260)
