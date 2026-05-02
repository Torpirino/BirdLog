"""Página de consulta de visitas."""

from __future__ import annotations

import datetime

import pandas as pd
import streamlit as st

from dashboard.lib.consultas import (
    cargar_tablas_consulta,
    meteorologia_de_visita,
    visitas_legibles,
)
from dashboard.lib.filtros import filtrar_fecha, filtrar_lugar, filtrar_valores, opciones_unicas
from dashboard.lib.ui import panel_filtros, rejilla_metricas, sin_datos, tabla_datos


TIPOS_VISITA = {
    "LINDUS": "Lindus",
    "CAJA_NIDO": "Cajas nido",
    "CEBO_AVISPON": "Cebos avispones",
    "NIDO_RAPAZ": "Nidos rapaces",
    "MAMIFEROS_PUENTES": "Mamíferos puentes",
    "IMPACTO_AMBIENTAL": "Impacto ambiental",
}


@st.cache_data(ttl=120)
def _cargar_datos() -> dict[str, pd.DataFrame]:
    """Carga tablas necesarias para consultar visitas."""
    return cargar_tablas_consulta()


def render() -> None:
    """Renderiza la página de visitas."""
    try:
        tablas = _cargar_datos()
    except Exception as exc:
        st.warning(f"No se pudieron cargar datos: {exc}")
        return

    visitas = visitas_legibles(tablas)
    if visitas.empty:
        sin_datos("Sin visitas todavía.")
        return

    visitas = _preparar_visitas(visitas)
    filtradas = _aplicar_filtros(visitas)
    _render_metricas(filtradas)
    _render_tabla_y_detalle(filtradas, tablas)


def _preparar_visitas(visitas: pd.DataFrame) -> pd.DataFrame:
    """Normaliza columnas legibles de visitas."""
    visitas = visitas.copy()
    if "tipo_visita" in visitas:
        visitas["tipo"] = visitas["tipo_visita"].map(TIPOS_VISITA).fillna(visitas["tipo_visita"])
    for columna in ["observaciones", "nombre_lugar", "nombre_observador"]:
        if columna in visitas:
            visitas[columna] = visitas[columna].apply(_limpiar_celda)
    return visitas


def _aplicar_filtros(visitas: pd.DataFrame) -> pd.DataFrame:
    """Dibuja filtros y devuelve visitas filtradas."""
    id_visita = _id_sesion("filtro_id_visita_visitas")
    if id_visita is not None:
        st.info(f"Filtro activo: visita #{id_visita}")
        if st.button("Limpiar filtro de visita", key="limpiar_filtro_visitas"):
            st.session_state.pop("filtro_id_visita_visitas", None)
            st.rerun()
        return visitas[visitas["id_visita"].astype("Int64") == id_visita]

    with panel_filtros():
        c1, c2, c3, c4 = st.columns(4)
        desde, hasta = _rango_fechas(c1, visitas)
        tipos = c2.multiselect("Tipo de visita", _tipos_disponibles(visitas))
        lugares = c3.multiselect("Lugar", opciones_unicas(visitas, "nombre_lugar"))
        observadores = c4.multiselect("Observador", opciones_unicas(visitas, "nombre_observador"))

    filtradas = filtrar_fecha(visitas, desde=desde, hasta=hasta)
    if tipos:
        tipos_tecnicos = [codigo for codigo, etiqueta in TIPOS_VISITA.items() if etiqueta in tipos]
        filtradas = filtrar_valores(filtradas, "tipo_visita", tipos_tecnicos)
    filtradas = filtrar_lugar(filtradas, lugares)
    return filtrar_valores(filtradas, "nombre_observador", observadores)


def _render_metricas(visitas: pd.DataFrame) -> None:
    """Muestra métricas compactas de visitas."""
    tipos = visitas["tipo_visita"].nunique() if "tipo_visita" in visitas else 0
    lugares = visitas["id_lugar"].nunique() if "id_lugar" in visitas else 0
    observadores = visitas["id_observador"].nunique() if "id_observador" in visitas else 0
    rejilla_metricas(
        [
            ("Visitas", str(len(visitas)) if len(visitas) else "Sin datos", "Visitas filtradas"),
            ("Tipos", str(tipos) if tipos else "Sin datos", "Tipos de visita"),
            ("Lugares", str(lugares) if lugares else "Sin datos", "Lugares visitados"),
            ("Observadores", str(observadores) if observadores else "Sin datos", "Observadores"),
        ]
    )


def _render_tabla_y_detalle(visitas: pd.DataFrame, tablas: dict[str, pd.DataFrame]) -> None:
    """Muestra tabla seleccionable y detalle de visita."""
    st.subheader("Listado de visitas")
    if visitas.empty:
        sin_datos("Sin visitas para los filtros seleccionados.")
        return

    visitas = visitas.reset_index(drop=True)
    col_tabla, col_detalle = st.columns([3, 2])
    with col_tabla:
        estado = st.dataframe(
            _tabla_visitas(visitas),
            on_select="rerun",
            selection_mode="single-row",
            use_container_width=True,
            height=430,
            hide_index=True,
            key="visitas_tabla",
        )
        filas = estado.selection.rows
    with col_detalle:
        id_filtrada = _id_sesion("filtro_id_visita_visitas")
        if id_filtrada is not None and not visitas.empty:
            _render_detalle_visita(visitas.iloc[0], tablas)
        elif filas:
            _render_detalle_visita(visitas.iloc[filas[0]], tablas)
        else:
            st.info("Selecciona una visita en la tabla para ver el detalle.")


def _tabla_visitas(visitas: pd.DataFrame) -> pd.DataFrame:
    """Prepara tabla de visitas para el usuario."""
    columnas = {
        "id_visita": "ID",
        "fecha": "Fecha",
        "tipo": "Tipo",
        "nombre_lugar": "Lugar",
        "nombre_observador": "Observador",
        "hora_inicio": "Inicio",
        "hora_fin": "Fin",
        "observaciones": "Observaciones",
    }
    df = visitas[[c for c in columnas if c in visitas]].rename(columns=columnas).copy()
    if "Fecha" in df:
        df["Fecha"] = df["Fecha"].apply(_formatear_fecha)
    for columna in ["Inicio", "Fin"]:
        if columna in df:
            df[columna] = df[columna].apply(_formatear_hora)
    for columna in ["Tipo", "Lugar", "Observador", "Observaciones"]:
        if columna in df:
            df[columna] = df[columna].apply(_limpiar_celda)
    return df


def _render_detalle_visita(visita: pd.Series, tablas: dict[str, pd.DataFrame]) -> None:
    """Muestra detalle de una visita y navegación a registros asociados."""
    id_visita = _id_valor(visita.get("id_visita"))
    with st.container(border=True):
        st.subheader(f"Visita #{id_visita}" if id_visita is not None else "Visita")
        _campo("Fecha", visita.get("fecha"))
        _campo("Tipo", visita.get("tipo"))
        _campo("Lugar", visita.get("nombre_lugar"))
        _campo("Observador", visita.get("nombre_observador"))
        _campo("Hora inicio", visita.get("hora_inicio"))
        _campo("Hora fin", visita.get("hora_fin"))
        _campo("Observaciones", visita.get("observaciones"))

        st.divider()
        st.caption("Meteorología de la visita")
        _render_meteo(meteorologia_de_visita(tablas, id_visita))

        st.divider()
        st.caption("Registros asociados")
        _render_resumen_registros(visita, tablas, id_visita)


def _render_resumen_registros(
    visita: pd.Series, tablas: dict[str, pd.DataFrame], id_visita: int | None
) -> None:
    """Muestra resumen de registros asociados a la visita."""
    tipo = visita.get("tipo_visita")
    if id_visita is None:
        st.info("No se puede resolver la visita seleccionada.")
        return
    if tipo == "LINDUS":
        datos = _registros_por_visita(tablas.get("lindus", pd.DataFrame()), id_visita)
        individuos = int(pd.to_numeric(datos.get("numero", pd.Series(dtype=int)), errors="coerce").fillna(0).sum())
        especies = datos["id_especie"].nunique() if "id_especie" in datos else 0
        _campo("Observaciones Lindus", len(datos))
        _campo("Individuos", individuos)
        _campo("Especies", especies)
        if st.button("Ver observaciones Lindus de esta visita", use_container_width=True):
            st.session_state["filtro_id_visita_lindus"] = id_visita
            st.session_state["pagina_activa"] = "Lindus"
            st.rerun()
        return
    _render_resumen_pendiente(tipo, tablas, id_visita)


def _render_resumen_pendiente(tipo: str, tablas: dict[str, pd.DataFrame], id_visita: int) -> None:
    """Deja preparado el patrón para páginas no conectadas todavía."""
    config = {
        "CAJA_NIDO": ("cajas_nido", "Revisiones de cajas", "Ver cajas nido de esta visita"),
        "CEBO_AVISPON": ("cebos_avispones", "Registros de cebos", "Ver cebos de esta visita"),
        "NIDO_RAPAZ": ("nidos_rapaces", "Revisiones de nidos", "Ver nidos rapaces de esta visita"),
        "MAMIFEROS_PUENTES": ("mamiferos_puentes", "Registros de mamíferos", "Ver mamíferos de esta visita"),
    }
    tabla, etiqueta, boton = config.get(tipo, ("", "Registros", "Ver registros de esta visita"))
    datos = _registros_por_visita(tablas.get(tabla, pd.DataFrame()), id_visita)
    _campo(etiqueta, len(datos))
    st.button(boton, disabled=True, use_container_width=True)
    st.caption("Navegación cruzada pendiente para esta página.")


def _render_meteo(meteo: pd.DataFrame) -> None:
    """Muestra meteorología de la visita."""
    if meteo.empty:
        st.info("Sin meteorología registrada para esta visita.")
        return
    nombres = {
        "hora": "Hora",
        "temperatura": "Temperatura",
        "nubosidad": "Nubosidad",
        "viento_direccion": "Dirección viento",
        "viento_intensidad": "Intensidad viento",
        "precipitacion": "Precipitación",
        "visibilidad": "Visibilidad",
    }
    df = meteo[[c for c in nombres if c in meteo]].rename(columns=nombres).copy()
    if "Hora" in df:
        df["Hora"] = df["Hora"].apply(_formatear_hora)
    tabla_datos(df, "Sin meteorología registrada para esta visita.")


def _rango_fechas(columna, visitas: pd.DataFrame):
    """Selector de rango de fechas para visitas."""
    fechas = pd.to_datetime(visitas["fecha"], errors="coerce").dropna().dt.date
    if fechas.empty:
        return None, None
    rango = columna.date_input("Fecha", value=(fechas.min(), fechas.max()), key="visitas_fecha")
    return rango if isinstance(rango, tuple) and len(rango) == 2 else (None, None)


def _tipos_disponibles(visitas: pd.DataFrame) -> list[str]:
    """Devuelve tipos humanos disponibles."""
    if visitas.empty or "tipo_visita" not in visitas:
        return []
    codigos = visitas["tipo_visita"].dropna().astype(str).sort_values().unique()
    return [TIPOS_VISITA.get(codigo, codigo) for codigo in codigos]


def _registros_por_visita(df: pd.DataFrame, id_visita: int) -> pd.DataFrame:
    """Filtra una tabla de registros por visita."""
    if df.empty or "id_visita" not in df:
        return pd.DataFrame()
    return df[df["id_visita"].astype("Int64") == id_visita]


def _campo(etiqueta: str, valor) -> None:
    """Muestra un campo con valor legible."""
    st.markdown(f"**{etiqueta}:** {_formatear_valor(valor)}")


def _formatear_valor(valor) -> str:
    """Formatea valores para detalle."""
    if valor is None:
        return "—"
    try:
        if pd.isna(valor):
            return "—"
    except (TypeError, ValueError):
        pass
    if isinstance(valor, (datetime.datetime, pd.Timestamp)):
        return valor.strftime("%d/%m/%Y")
    if isinstance(valor, datetime.date):
        return valor.strftime("%d/%m/%Y")
    if isinstance(valor, datetime.time):
        return valor.strftime("%H:%M")
    texto = _limpiar_celda(valor)
    if len(texto) >= 10 and texto[4:5] == "-" and texto[7:8] == "-":
        try:
            return datetime.date.fromisoformat(texto[:10]).strftime("%d/%m/%Y")
        except ValueError:
            pass
    if len(texto) >= 5 and texto[2:3] == ":":
        return texto[:5]
    return texto or "—"


def _formatear_fecha(valor) -> str:
    """Formatea fecha DD/MM/YYYY."""
    texto = _formatear_valor(valor)
    return "" if texto == "—" else texto


def _formatear_hora(valor) -> str:
    """Formatea hora HH:MM."""
    texto = _formatear_valor(valor)
    return "" if texto == "—" else texto[:5]


def _limpiar_celda(valor) -> str:
    """Limpia marcadores técnicos y nulos."""
    if valor is None:
        return ""
    try:
        if pd.isna(valor):
            return ""
    except (TypeError, ValueError):
        pass
    texto = str(valor).replace("[SINTETICO_TEST]", "").strip()
    return "" if texto.lower() in {"none", "nan", "nat", "<na>"} else texto


def _id_sesion(clave: str) -> int | None:
    """Lee un id de visita desde session_state."""
    return _id_valor(st.session_state.get(clave))


def _id_valor(valor) -> int | None:
    """Convierte un valor a entero de id si es posible."""
    try:
        if valor is None or pd.isna(valor):
            return None
    except (TypeError, ValueError):
        pass
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None
