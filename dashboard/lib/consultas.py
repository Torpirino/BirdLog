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


def _cargar_tabla_paginada(tabla: str, columnas: str, tamano_pagina: int = 1000) -> pd.DataFrame:
    """Carga una tabla paginando para no perder filas."""
    cliente = get_cliente()
    partes = []
    inicio = 0
    while True:
        fin = inicio + tamano_pagina - 1
        respuesta = cliente.table(tabla).select(columnas).range(inicio, fin).execute()
        df = respuesta_a_dataframe(respuesta)
        if df.empty:
            break
        partes.append(df)
        if len(df) < tamano_pagina:
            break
        inicio += tamano_pagina
    return pd.concat(partes, ignore_index=True) if partes else pd.DataFrame()


def cargar_tabla(tabla: str, columnas: str = "*", limite: int | None = None) -> pd.DataFrame:
    """Carga una tabla completa o limitada desde Supabase."""
    if tabla not in TABLAS:
        raise ValueError(f"Tabla no permitida para dashboard: {tabla}")
    if limite is not None:
        consulta = get_cliente().table(tabla).select(columnas).limit(limite)
        return respuesta_a_dataframe(consulta.execute())
    return _cargar_tabla_paginada(tabla, columnas)


def cargar_tablas(tablas: list[str] | None = None) -> dict[str, pd.DataFrame]:
    """Carga varias tablas y las devuelve por nombre."""
    return {tabla: cargar_tabla(tabla) for tabla in (tablas or TABLAS)}


def cargar_tablas_dashboard() -> dict[str, pd.DataFrame]:
    """Carga las tablas necesarias para inicio y mapa."""
    return cargar_tablas(
        [
            "especies",
            "observadores",
            "lugares",
            "visitas",
            "lindus",
            "cajas_nido",
            "nidos_rapaces",
            "cebos_avispones",
            "mamiferos_puentes",
            "fotos",
        ]
    )


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


def metricas_inicio(tablas: dict[str, pd.DataFrame]) -> list[tuple[str, str, str]]:
    """Calcula métricas principales de la portada."""
    visitas = tablas.get("visitas", pd.DataFrame())
    lindus = tablas.get("lindus", pd.DataFrame())
    cajas = tablas.get("cajas_nido", pd.DataFrame())
    cebos = tablas.get("cebos_avispones", pd.DataFrame())
    mamiferos = tablas.get("mamiferos_puentes", pd.DataFrame())
    lugares = tablas.get("lugares", pd.DataFrame())
    return [
        ("Total visitas", _numero(len(visitas)), "Visitas registradas"),
        ("Última visita", _ultima_fecha(visitas), "Fecha más reciente"),
        ("Especies observadas", _numero(_total_especies_observadas(tablas)), "Especies con registros"),
        ("Lugares activos", _numero(len(lugares)), "Lugares en catálogo"),
        ("Observaciones Lindus", _numero(len(lindus)), "Registros de paso migratorio"),
        ("Cajas ocupadas", _numero(_contar_ocupadas(cajas)), "Revisiones con caja ocupada"),
        ("Capturas vv", _numero(_sumar_columna(cebos, "vv")), "Vespa velutina acumulada"),
        ("Mamíferos detectados", _numero(mamiferos["id_especie"].nunique() if "id_especie" in mamiferos else 0), "Especies con presencia"),
    ]


def ranking_especies(tablas: dict[str, pd.DataFrame], limite: int = 10) -> pd.DataFrame:
    """Crea ranking de especies registradas en tablas biológicas."""
    especies = tablas.get("especies", pd.DataFrame())
    ids = _serie_ids_especies(tablas)
    if ids.empty:
        return pd.DataFrame(columns=["id_especie", "registros"])
    ranking = ids.value_counts().reset_index()
    ranking.columns = ["id_especie", "registros"]
    ranking = unir_nombre_especie(ranking, especies)
    if "nombre_comun" in ranking.columns:
        ranking["especie"] = ranking["nombre_comun"].fillna(ranking.get("nombre_cientifico"))
    else:
        ranking["especie"] = ranking["id_especie"].astype(str)
    return ranking.head(limite)


def ultimos_registros(tablas: dict[str, pd.DataFrame], limite: int = 8) -> pd.DataFrame:
    """Combina últimos registros de las tablas biológicas."""
    registros = [
        _registros_tabla(tablas, "lindus", "Lindus"),
        _registros_tabla(tablas, "cajas_nido", "Caja nido"),
        _registros_tabla(tablas, "nidos_rapaces", "Nido rapaz"),
        _registros_tabla(tablas, "cebos_avispones", "Cebo avispón"),
        _registros_tabla(tablas, "mamiferos_puentes", "Mamífero puente"),
    ]
    columnas = ["fecha", "tipo", "nombre_lugar", "nombre_lugar_visita", "especie", "observaciones"]
    registros = [df for df in registros if not df.empty]
    if not registros:
        return pd.DataFrame(columns=columnas)
    datos = pd.concat(registros, ignore_index=True)
    if datos.empty:
        return pd.DataFrame(columns=columnas)
    return ordenar_por_fecha(datos).head(limite)[[c for c in columnas if c in datos.columns]]


def lugares_con_actividad(
    tablas: dict[str, pd.DataFrame],
    desde: Any = None,
    hasta: Any = None,
    especies: list[str] | None = None,
) -> pd.DataFrame:
    """Devuelve lugares, opcionalmente restringidos por actividad biológica."""
    lugares = tablas.get("lugares", pd.DataFrame())
    ids = _ids_lugares_actividad(tablas, desde, hasta, especies or [])
    if lugares.empty or ids is None:
        return lugares
    return lugares[lugares["id_lugar"].isin(ids)]


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


def _registros_tabla(tablas: dict[str, pd.DataFrame], tabla: str, tipo: str) -> pd.DataFrame:
    """Prepara registros recientes de una tabla."""
    datos = observaciones_legibles(tabla, tablas)
    if datos.empty:
        return datos
    datos = datos.copy()
    datos["tipo"] = tipo
    if "nombre_comun" in datos.columns:
        alternativa = datos["nombre_cientifico"] if "nombre_cientifico" in datos.columns else ""
        datos["especie"] = datos["nombre_comun"].fillna(alternativa)
    return datos


def _ids_lugares_actividad(
    tablas: dict[str, pd.DataFrame], desde: Any, hasta: Any, especies: list[str]
) -> set[int] | None:
    """Calcula ids de lugar con actividad tras filtros."""
    if not desde and not hasta and not especies:
        return None
    ids_especies = _ids_especies_por_nombre(tablas.get("especies", pd.DataFrame()), especies)
    visitas = _filtrar_visitas_fecha(visitas_legibles(tablas), desde, hasta)
    filtra_fecha = bool(desde or hasta)
    ids_visitas = set(visitas["id_visita"]) if "id_visita" in visitas else set()
    if filtra_fecha and not ids_visitas:
        return set()
    ids_lugares = set()
    if filtra_fecha and not especies and "id_lugar" in visitas:
        ids_lugares = set(visitas["id_lugar"])
    for tabla in ["lindus", "cajas_nido", "nidos_rapaces", "mamiferos_puentes"]:
        ids_lugares.update(_ids_lugares_tabla(tablas, tabla, ids_visitas if filtra_fecha else None, ids_especies))
    return ids_lugares


def _ids_lugares_tabla(
    tablas: dict[str, pd.DataFrame], tabla: str, ids_visitas: set[int] | None, ids_especies: set[int] | None
) -> set[int]:
    """Obtiene lugares de una tabla específica."""
    df = tablas.get(tabla, pd.DataFrame())
    if df.empty:
        return set()
    if ids_visitas is not None and "id_visita" in df:
        df = df[df["id_visita"].isin(ids_visitas)]
    if ids_especies is not None and "id_especie" in df:
        df = df[df["id_especie"].isin(ids_especies)]
    if "id_lugar" in df:
        return set(df["id_lugar"].dropna().astype(int))
    return set(_visitas_a_lugares(tablas, df))


def _visitas_a_lugares(tablas: dict[str, pd.DataFrame], df: pd.DataFrame) -> pd.Series:
    """Traduce ids de visita a ids de lugar."""
    visitas = tablas.get("visitas", pd.DataFrame())
    if visitas.empty or "id_visita" not in df or "id_lugar" not in visitas:
        return pd.Series(dtype=int)
    return df[["id_visita"]].merge(visitas[["id_visita", "id_lugar"]], on="id_visita", how="left")["id_lugar"].dropna()


def _filtrar_visitas_fecha(visitas: pd.DataFrame, desde: Any, hasta: Any) -> pd.DataFrame:
    """Filtra visitas por fecha."""
    if visitas.empty or "fecha" not in visitas:
        return visitas
    fechas = pd.to_datetime(visitas["fecha"], errors="coerce").dt.date
    if desde:
        visitas = visitas[fechas >= desde]
        fechas = pd.to_datetime(visitas["fecha"], errors="coerce").dt.date
    if hasta:
        visitas = visitas[fechas <= hasta]
    return visitas


def _ids_especies_por_nombre(especies: pd.DataFrame, nombres: list[str]) -> set[int] | None:
    """Resuelve nombres de especies a ids."""
    nombres = [nombre for nombre in nombres if nombre]
    if not nombres:
        return None
    if especies.empty:
        return set()
    mascara = pd.Series(False, index=especies.index)
    for columna in ["nombre_comun", "nombre_cientifico"]:
        if columna in especies:
            mascara = mascara | especies[columna].astype(str).isin(nombres)
    return set(especies.loc[mascara, "id_especie"].dropna().astype(int))


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


def _numero(valor: int | float) -> str:
    """Formatea números o devuelve Sin datos."""
    return "Sin datos" if valor == 0 else f"{int(valor):,}".replace(",", ".")


def _ultima_fecha(visitas: pd.DataFrame) -> str:
    """Devuelve última fecha de visita."""
    if visitas.empty or "fecha" not in visitas.columns:
        return "Sin datos"
    fecha = pd.to_datetime(visitas["fecha"], errors="coerce").max()
    return "Sin datos" if pd.isna(fecha) else fecha.strftime("%d/%m/%Y")


def _sumar_columna(df: pd.DataFrame, columna: str) -> int:
    """Suma una columna numérica si existe."""
    if df.empty or columna not in df.columns:
        return 0
    return int(pd.to_numeric(df[columna], errors="coerce").fillna(0).sum())


def _contar_ocupadas(cajas: pd.DataFrame) -> int:
    """Cuenta cajas marcadas como ocupadas."""
    if cajas.empty or "ocupada" not in cajas.columns:
        return 0
    return int(cajas["ocupada"].fillna(False).astype(bool).sum())


def _serie_ids_especies(tablas: dict[str, pd.DataFrame]) -> pd.Series:
    """Combina ids de especie de tablas biológicas."""
    series = []
    for tabla in ["lindus", "cajas_nido", "nidos_rapaces", "mamiferos_puentes"]:
        df = tablas.get(tabla, pd.DataFrame())
        if not df.empty and "id_especie" in df.columns:
            series.append(df["id_especie"].dropna())
    return pd.concat(series, ignore_index=True) if series else pd.Series(dtype=int)


def _total_especies_observadas(tablas: dict[str, pd.DataFrame]) -> int:
    """Cuenta especies con al menos un registro biológico."""
    ids = _serie_ids_especies(tablas)
    return 0 if ids.empty else int(ids.nunique())
