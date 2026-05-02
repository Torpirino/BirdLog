"""Filtros compartidos para páginas del dashboard."""

from collections.abc import Iterable
from datetime import date

import pandas as pd


def opciones_unicas(df: pd.DataFrame, columna: str) -> list[str]:
    """Devuelve opciones únicas limpias para selectores."""
    if df.empty or columna not in df.columns:
        return []
    valores = df[columna].dropna().astype(str).sort_values().unique()
    return valores.tolist()


def filtrar_fecha(
    df: pd.DataFrame, columna: str = "fecha", desde: date | None = None, hasta: date | None = None
) -> pd.DataFrame:
    """Filtra por rango de fechas inclusivo."""
    if df.empty or columna not in df.columns:
        return df
    filtrado = df.copy()
    fechas = pd.to_datetime(filtrado[columna], errors="coerce").dt.date
    if desde is not None:
        filtrado = filtrado[fechas >= desde]
        fechas = pd.to_datetime(filtrado[columna], errors="coerce").dt.date
    if hasta is not None:
        filtrado = filtrado[fechas <= hasta]
    return filtrado


def filtrar_valores(df: pd.DataFrame, columna: str, valores: Iterable[str] | None) -> pd.DataFrame:
    """Filtra por una lista de valores si se proporciona."""
    valores_limpios = [v for v in (valores or []) if v]
    if df.empty or columna not in df.columns or not valores_limpios:
        return df
    return df[df[columna].astype(str).isin(valores_limpios)]


def filtrar_especie(df: pd.DataFrame, especies: Iterable[str] | None) -> pd.DataFrame:
    """Filtra por nombre común, científico o id de especie."""
    columna = _primera_columna(df, ["nombre_comun", "nombre_cientifico", "id_especie"])
    return filtrar_valores(df, columna, especies) if columna else df


def filtrar_lugar(df: pd.DataFrame, lugares: Iterable[str] | None) -> pd.DataFrame:
    """Filtra por nombre o id de lugar."""
    columna = _primera_columna(df, ["nombre_lugar", "id_lugar"])
    return filtrar_valores(df, columna, lugares) if columna else df


def filtrar_tipo(df: pd.DataFrame, tipos: Iterable[str] | None) -> pd.DataFrame:
    """Filtra por tipo de visita o tipo de lugar."""
    columna = _primera_columna(df, ["tipo_visita", "tipo_lugar"])
    return filtrar_valores(df, columna, tipos) if columna else df


def filtrar_rango_numerico(
    df: pd.DataFrame, columna: str, minimo: int | float | None, maximo: int | float | None
) -> pd.DataFrame:
    """Filtra una columna numérica por rango inclusivo."""
    if df.empty or columna not in df.columns:
        return df
    serie = pd.to_numeric(df[columna], errors="coerce")
    filtrado = df
    if minimo is not None:
        filtrado = filtrado[serie >= minimo]
        serie = pd.to_numeric(filtrado[columna], errors="coerce")
    if maximo is not None:
        filtrado = filtrado[serie <= maximo]
    return filtrado


def aplicar_filtros_basicos(
    df: pd.DataFrame,
    desde: date | None = None,
    hasta: date | None = None,
    especies: Iterable[str] | None = None,
    lugares: Iterable[str] | None = None,
    tipos: Iterable[str] | None = None,
) -> pd.DataFrame:
    """Aplica filtros frecuentes de fecha, especie, lugar y tipo."""
    filtrado = filtrar_fecha(df, desde=desde, hasta=hasta)
    filtrado = filtrar_especie(filtrado, especies)
    filtrado = filtrar_lugar(filtrado, lugares)
    return filtrar_tipo(filtrado, tipos)


def _primera_columna(df: pd.DataFrame, candidatas: list[str]) -> str | None:
    """Devuelve la primera columna existente."""
    return next((columna for columna in candidatas if columna in df.columns), None)
