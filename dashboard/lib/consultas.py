"""Consultas reutilizables para el dashboard."""

from functools import reduce
from typing import Any

import pandas as pd

from dashboard.lib.conexion import get_cliente


TABLAS = [
    "especies",
    "observadores",
    "lugares",
    "visitas",
    "meteorologia",
    "lindus",
    "cajas_nido",
    "nidos_rapaces",
    "cebos_avispones",
    "mamiferos_puentes",
    "fotos",
]

ID_TABLA = {
    "especies": "id_especie",
    "observadores": "id_observador",
    "lugares": "id_lugar",
    "visitas": "id_visita",
    "meteorologia": "id_meteo",
    "lindus": "id_lindus",
    "cajas_nido": "id_cajanido",
    "nidos_rapaces": "id_nido_rapaz",
    "cebos_avispones": "id_cebo",
    "mamiferos_puentes": "id_mamifero",
    "fotos": "id_foto",
}


def respuesta_a_dataframe(respuesta: Any) -> pd.DataFrame:
    """Convierte una respuesta Supabase en DataFrame."""
    datos = getattr(respuesta, "data", respuesta) or []
    return pd.DataFrame(datos)


def cargar_tabla(tabla: str, columnas: str = "*", limite: int | None = None) -> pd.DataFrame:
    """Carga una tabla completa o limitada desde Supabase."""
    if tabla not in TABLAS:
        raise ValueError(f"Tabla no permitida para dashboard: {tabla}")
    consulta = get_cliente().table(tabla).select(columnas)
    if limite is not None:
        consulta = consulta.limit(limite)
    return respuesta_a_dataframe(consulta.execute())


def cargar_tablas(tablas: list[str] | None = None) -> dict[str, pd.DataFrame]:
    """Carga varias tablas y las devuelve por nombre."""
    return {tabla: cargar_tabla(tabla) for tabla in (tablas or TABLAS)}


def ordenar_por_fecha(df: pd.DataFrame, columna: str = "fecha") -> pd.DataFrame:
    """Ordena de reciente a antiguo si existe la columna."""
    if df.empty or columna not in df.columns:
        return df
    ordenado = df.copy()
    ordenado[columna] = pd.to_datetime(ordenado[columna], errors="coerce")
    return ordenado.sort_values(columna, ascending=False, na_position="last")


def unir_nombre_lugar(df: pd.DataFrame, lugares: pd.DataFrame) -> pd.DataFrame:
    """Añade nombre de lugar y municipio a un DataFrame con id_lugar."""
    columnas = ["id_lugar", "nombre_lugar", "tipo_lugar", "municipio", "utm_x", "utm_y"]
    return _unir_catalogo(df, lugares, "id_lugar", [c for c in columnas if c in lugares])


def unir_nombre_especie(df: pd.DataFrame, especies: pd.DataFrame) -> pd.DataFrame:
    """Añade nombre común, científico y grupo a un DataFrame con id_especie."""
    columnas = ["id_especie", "nombre_comun", "nombre_cientifico", "grupo"]
    return _unir_catalogo(df, especies, "id_especie", [c for c in columnas if c in especies])


def unir_nombre_observador(df: pd.DataFrame, observadores: pd.DataFrame) -> pd.DataFrame:
    """Añade nombre del observador a un DataFrame con id_observador."""
    columnas = ["id_observador", "nombre_observador"]
    return _unir_catalogo(df, observadores, "id_observador", [c for c in columnas if c in observadores])


def visitas_legibles(tablas: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Devuelve visitas con lugar y observador legibles."""
    visitas = tablas.get("visitas", pd.DataFrame())
    if visitas.empty:
        return visitas
    visitas = unir_nombre_lugar(visitas, tablas.get("lugares", pd.DataFrame()))
    visitas = unir_nombre_observador(visitas, tablas.get("observadores", pd.DataFrame()))
    return ordenar_por_fecha(visitas)


def observaciones_legibles(tabla: str, tablas: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Une una tabla específica con visitas, lugares, observadores y especies."""
    df = tablas.get(tabla, pd.DataFrame())
    if df.empty:
        return df
    df = unir_visita(df, visitas_legibles(tablas))
    if "id_lugar" in df.columns:
        df = unir_nombre_lugar(df, tablas.get("lugares", pd.DataFrame()))
    if "id_especie" in df.columns:
        df = unir_nombre_especie(df, tablas.get("especies", pd.DataFrame()))
    return ordenar_por_fecha(df)


def unir_visita(df: pd.DataFrame, visitas: pd.DataFrame) -> pd.DataFrame:
    """Añade datos de visita a una tabla con id_visita."""
    if df.empty or visitas.empty or "id_visita" not in df.columns:
        return df
    columnas = [
        "id_visita",
        "fecha",
        "hora_inicio",
        "hora_fin",
        "tipo_visita",
        "nombre_lugar",
        "nombre_observador",
    ]
    visita = visitas[[c for c in columnas if c in visitas]].drop_duplicates("id_visita")
    visita = visita.rename(columns={"nombre_lugar": "nombre_lugar_visita"})
    return df.merge(visita, on="id_visita", how="left")


def conteo_por(df: pd.DataFrame, columna: str, nombre_valor: str = "total") -> pd.DataFrame:
    """Cuenta filas por una columna y devuelve un DataFrame ordenado."""
    if df.empty or columna not in df.columns:
        return pd.DataFrame(columns=[columna, nombre_valor])
    return df.groupby(columna, dropna=False).size().reset_index(name=nombre_valor)


def sumar_por(df: pd.DataFrame, grupo: str, columna: str, nombre_valor: str = "total") -> pd.DataFrame:
    """Suma una columna numérica por grupo."""
    if df.empty or not {grupo, columna}.issubset(df.columns):
        return pd.DataFrame(columns=[grupo, nombre_valor])
    return df.groupby(grupo, dropna=False)[columna].sum().reset_index(name=nombre_valor)


def _unir_catalogo(
    df: pd.DataFrame, catalogo: pd.DataFrame, clave: str, columnas: list[str]
) -> pd.DataFrame:
    """Une un catálogo sin fallar si faltan datos."""
    if df.empty or catalogo.empty or clave not in df.columns or clave not in catalogo.columns:
        return df
    return df.merge(catalogo[columnas].drop_duplicates(clave), on=clave, how="left")


def unir_catalogos(df: pd.DataFrame, uniones: list[tuple[pd.DataFrame, str, list[str]]]) -> pd.DataFrame:
    """Aplica varias uniones de catálogo en orden."""
    return reduce(lambda actual, union: _unir_catalogo(actual, *union), uniones, df)
