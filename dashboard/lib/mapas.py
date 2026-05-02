"""Mapas Folium y transformación de coordenadas."""

from typing import Any

import folium
import pandas as pd
from pyproj import Transformer


EPSG_UTM_DEFAULT = 25830
EPSG_LATLON = 4326
CENTRO_NAVARRA = (42.8, -1.65)


def convertir_utm_a_latlon(
    utm_x: float, utm_y: float, epsg_origen: int = EPSG_UTM_DEFAULT
) -> tuple[float, float]:
    """Convierte coordenadas UTM a lat/lon."""
    transformer = Transformer.from_crs(epsg_origen, EPSG_LATLON, always_xy=True)
    lon, lat = transformer.transform(utm_x, utm_y)
    return lat, lon


def anadir_latlon(
    df: pd.DataFrame,
    columna_x: str = "utm_x",
    columna_y: str = "utm_y",
    epsg_origen: int = EPSG_UTM_DEFAULT,
) -> pd.DataFrame:
    """Añade columnas lat y lon a partir de UTM."""
    if df.empty or not {columna_x, columna_y}.issubset(df.columns):
        return df
    datos = df.copy()
    coords = datos.apply(
        lambda fila: convertir_utm_a_latlon(fila[columna_x], fila[columna_y], epsg_origen),
        axis=1,
    )
    datos[["lat", "lon"]] = pd.DataFrame(coords.tolist(), index=datos.index)
    return datos


def crear_mapa_base(
    centro: tuple[float, float] = CENTRO_NAVARRA, zoom: int = 9, tiles: str = "CartoDB positron"
) -> folium.Map:
    """Crea un mapa base limpio."""
    return folium.Map(location=centro, zoom_start=zoom, tiles=tiles, control_scale=True)


def capa_marcadores(
    mapa: folium.Map,
    df: pd.DataFrame,
    nombre: str,
    color: str = "green",
    popup_columnas: list[str] | None = None,
) -> folium.FeatureGroup:
    """Añade una capa de marcadores desde columnas lat/lon."""
    capa = folium.FeatureGroup(name=nombre, show=True)
    if not df.empty and {"lat", "lon"}.issubset(df.columns):
        for _, fila in df.dropna(subset=["lat", "lon"]).iterrows():
            folium.Marker(
                location=(fila["lat"], fila["lon"]),
                popup=_popup(fila, popup_columnas),
                icon=folium.Icon(color=color, icon="leaf", prefix="fa"),
            ).add_to(capa)
    capa.add_to(mapa)
    return capa


def mapa_lugares(
    lugares: pd.DataFrame,
    nombre_capa: str = "Lugares",
    epsg_origen: int = EPSG_UTM_DEFAULT,
) -> folium.Map:
    """Crea un mapa con una capa de lugares."""
    datos = anadir_latlon(lugares, epsg_origen=epsg_origen)
    mapa = crear_mapa_base(_centro_desde_datos(datos))
    capa_marcadores(mapa, datos, nombre_capa, popup_columnas=_columnas_popup_lugar(datos))
    folium.LayerControl(collapsed=False).add_to(mapa)
    return mapa


def _centro_desde_datos(df: pd.DataFrame) -> tuple[float, float]:
    """Calcula centro si hay coordenadas."""
    if df.empty or not {"lat", "lon"}.issubset(df.columns):
        return CENTRO_NAVARRA
    return float(df["lat"].mean()), float(df["lon"].mean())


def _columnas_popup_lugar(df: pd.DataFrame) -> list[str]:
    """Columnas útiles para popup de lugares."""
    columnas = ["nombre_lugar", "tipo_lugar", "municipio", "utm_x", "utm_y"]
    return [columna for columna in columnas if columna in df.columns]


def _popup(fila: pd.Series, columnas: list[str] | None) -> str:
    """Construye popup HTML pequeño y controlado."""
    partes: list[str] = []
    for columna in columnas or []:
        valor: Any = fila.get(columna, "")
        partes.append(f"<b>{columna}</b>: {valor}")
    return "<br>".join(partes)
