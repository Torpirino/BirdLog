"""Utilidades para fotos asociadas."""

import pandas as pd

from dashboard.lib.consultas import cargar_tabla


def cargar_fotos() -> pd.DataFrame:
    """Carga la tabla fotos."""
    return cargar_tabla("fotos")


def filtrar_fotos_asociadas(
    fotos: pd.DataFrame,
    id_visita: int | None = None,
    tabla_origen: str | None = None,
    id_origen: int | None = None,
) -> pd.DataFrame:
    """Filtra fotos por visita, tabla de origen e id de origen."""
    if fotos.empty:
        return fotos
    mascara = pd.Series(False, index=fotos.index)
    if id_visita is not None and "id_visita" in fotos.columns:
        mascara = mascara | (fotos["id_visita"] == id_visita)
    if tabla_origen and id_origen is not None and {"tabla_origen", "id_origen"}.issubset(fotos.columns):
        mascara = mascara | ((fotos["tabla_origen"] == tabla_origen) & (fotos["id_origen"] == id_origen))
    return fotos[mascara]


def obtener_fotos_asociadas(
    id_visita: int | None = None,
    tabla_origen: str | None = None,
    id_origen: int | None = None,
) -> pd.DataFrame:
    """Carga y filtra fotos asociadas a un registro."""
    return filtrar_fotos_asociadas(cargar_fotos(), id_visita, tabla_origen, id_origen)


def tiene_fotos(
    fotos: pd.DataFrame, id_visita: int | None = None, tabla_origen: str | None = None, id_origen: int | None = None
) -> bool:
    """Indica si existen fotos para un registro."""
    return not filtrar_fotos_asociadas(fotos, id_visita, tabla_origen, id_origen).empty


def enlaces_drive(fotos: pd.DataFrame) -> list[dict[str, str]]:
    """Devuelve enlaces preparados para mostrar en Streamlit."""
    if fotos.empty or "url_drive" not in fotos.columns:
        return []
    enlaces = []
    for _, fila in fotos.iterrows():
        enlaces.append(
            {
                "url": str(fila.get("url_drive", "")),
                "descripcion": str(fila.get("descripcion") or "Foto sin descripción"),
            }
        )
    return enlaces
