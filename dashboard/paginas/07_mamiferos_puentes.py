"""Página de consulta de mamíferos en puentes."""

import datetime
from datetime import time

import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from dashboard.lib.consultas import cargar_tablas_consulta, meteorologia_de_visita, observaciones_legibles
from dashboard.lib.filtros import filtrar_fecha, filtrar_lugar, filtrar_valores, opciones_unicas
from dashboard.lib.fotos import enlaces_drive, filtrar_fotos_asociadas
from dashboard.lib.graficos import grafico_barras
from dashboard.lib.mapas import mapa_lugares
from dashboard.lib.ui import bloque_grafico, mostrar_enlaces_fotos, panel_filtros, rejilla_metricas, sin_datos, tabla_datos


_PRESENCIA_HUMANA = {
    "PRESENTE": "Presente",
    "AUSENTE": "Ausente",
    "POSIBLE": "Posible",
}

_EVIDENCIA_HUMANA = {
    "HUELLA": "Huella",
    "EXCREMENTO": "Excremento",
    "MADRIGUERA": "Madriguera",
    "AVISTAMIENTO": "Avistamiento",
}


@st.cache_data(ttl=120)
def _cargar_datos() -> dict[str, pd.DataFrame]:
    """Carga datos de mamíferos."""
    return cargar_tablas_consulta()


def render() -> None:
    """Renderiza la página de mamíferos puentes."""
    try:
        tablas = _cargar_datos()
    except Exception as exc:
        st.warning(f"No se pudieron cargar datos: {exc}")
        return
    datos = observaciones_legibles("mamiferos_puentes", tablas)
    if datos.empty:
        sin_datos("Sin datos de mamíferos en puentes todavía.")
        return
    filtrados = _render_filtros(datos)
    _render_metricas(filtrados)
    _render_graficos(filtrados)
    _render_mapa(filtrados)
    _render_tabla_y_detalle(filtrados, tablas)


def _render_filtros(datos: pd.DataFrame) -> pd.DataFrame:
    """Dibuja filtros de mamíferos."""
    id_visita = _id_sesion("filtro_id_visita_mamiferos_puentes")
    if id_visita is not None:
        st.info(f"Filtro activo: visita #{id_visita}")
        if st.button("Limpiar filtro de visita", key="limpiar_filtro_mamiferos"):
            st.session_state.pop("filtro_id_visita_mamiferos_puentes", None)
            st.rerun()
        datos = datos[datos["id_visita"].astype("Int64") == id_visita]

    with panel_filtros():
        c1, c2, c3 = st.columns(3)
        desde, hasta = _rango_fechas(c1, datos)
        especies = c2.multiselect("Especie", opciones_unicas(datos, "nombre_comun"))
        lugares = c3.multiselect("Puente", opciones_unicas(datos, "nombre_lugar"))
        c4, c5 = st.columns(2)
        presencias = c4.multiselect("Presencia", opciones_unicas(datos, "presencia"))
        evidencias = c5.multiselect("Tipo de evidencia", opciones_unicas(datos, "tipo_evidencia"))
    filtrados = filtrar_fecha(datos, desde=desde, hasta=hasta)
    filtrados = filtrar_valores(filtrados, "nombre_comun", especies)
    filtrados = filtrar_lugar(filtrados, lugares)
    filtrados = filtrar_valores(filtrados, "presencia", presencias)
    return filtrar_valores(filtrados, "tipo_evidencia", evidencias)


def _render_metricas(datos: pd.DataFrame) -> None:
    """Métricas de mamíferos."""
    especies = datos["id_especie"].nunique() if "id_especie" in datos else 0
    puentes = datos["id_lugar"].nunique() if "id_lugar" in datos else 0
    presentes = len(datos[datos["presencia"] == "PRESENTE"]) if "presencia" in datos else 0
    rejilla_metricas(
        [
            ("Detecciones", str(len(datos)) if len(datos) else "Sin datos", "Registros filtrados"),
            ("Especies", str(especies) if especies else "Sin datos", "Especies detectadas"),
            ("Puentes", str(puentes) if puentes else "Sin datos", "Puentes con datos"),
            ("Presentes", str(presentes) if presentes else "Sin datos", "Registros PRESENTE"),
        ]
    )


def _render_graficos(datos: pd.DataFrame) -> None:
    """Gráficos de mamíferos."""
    col1, col2 = st.columns(2)
    with col1:
        _grafico(_conteo(datos, "tipo_evidencia"), "tipo_evidencia", "total", "Evidencias")
        _grafico(_diversidad_por_puente(datos), "nombre_lugar", "especies", "Ranking de puentes por diversidad")
    with col2:
        _grafico(_conteo(datos, "presencia"), "presencia", "total", "Resumen por presencia")
        _grafico(_especies_por_puente(datos), "nombre_lugar", "registros", "Especies por puente")


def _render_mapa(datos: pd.DataFrame) -> None:
    """Mapa de puentes por especie filtrada."""
    st.subheader("Mapa de puentes")
    lugares = datos.drop_duplicates("id_lugar") if "id_lugar" in datos else pd.DataFrame()
    if lugares.empty:
        st.info("Sin coordenadas de puentes para los filtros.")
        return
    st_folium(mapa_lugares(lugares, "Mamíferos puentes"), use_container_width=True, height=460)


def _render_tabla_y_detalle(datos: pd.DataFrame, tablas: dict[str, pd.DataFrame]) -> None:
    """Tabla seleccionable a la izquierda y ficha de detalle a la derecha."""
    st.subheader("Detecciones")
    if datos.empty:
        sin_datos("Sin detecciones para los filtros.")
        return
    col_lista, col_detalle = st.columns([3, 2])
    with col_lista:
        df_display = _preparar_tabla(datos)
        estado = st.dataframe(
            df_display,
            on_select="rerun",
            selection_mode="single-row",
            use_container_width=True,
            height=420,
            hide_index=True,
            key="mamiferos_tabla",
        )
        filas = estado.selection.rows
    with col_detalle:
        if not filas:
            st.info("Selecciona un registro en la tabla para ver el detalle.")
        else:
            _render_detalle(datos.iloc[filas[0]], tablas)


def _preparar_tabla(datos: pd.DataFrame) -> pd.DataFrame:
    """Prepara DataFrame limpio para la tabla de detecciones."""
    mapa = {
        "fecha": "Fecha",
        "nombre_lugar": "Puente / Lugar",
        "nombre_comun": "Especie",
        "presencia": "Presencia",
        "tipo_evidencia": "Evidencia",
        "nombre_observador": "Observador",
        "observaciones": "Observaciones",
    }
    cols = [c for c in mapa if c in datos.columns]
    df = datos[cols].copy().rename(columns=mapa)
    if "Fecha" in df.columns:
        df["Fecha"] = (
            pd.to_datetime(df["Fecha"], errors="coerce")
            .dt.strftime("%d/%m/%Y")
            .fillna("")
        )
    if "Presencia" in df.columns:
        df["Presencia"] = df["Presencia"].apply(
            lambda v: _PRESENCIA_HUMANA.get(str(v).strip(), _limpiar_celda(v))
        )
    if "Evidencia" in df.columns:
        df["Evidencia"] = df["Evidencia"].apply(
            lambda v: _EVIDENCIA_HUMANA.get(str(v).strip(), _limpiar_celda(v))
        )
    for col in ("Puente / Lugar", "Especie", "Observador", "Observaciones"):
        if col in df.columns:
            df[col] = df[col].apply(_limpiar_celda)
    return df.reset_index(drop=True)


def _render_detalle(registro: pd.Series, tablas: dict[str, pd.DataFrame]) -> None:
    """Ficha de detalle de un registro de mamífero en puente."""
    id_visita = _id_valor(registro.get("id_visita"))
    with st.container(border=True):
        st.subheader("Detalle de registro")
        _campo("Puente / Lugar", registro.get("nombre_lugar"))
        _campo("Fecha", registro.get("fecha"))
        _campo("Especie", registro.get("nombre_comun") or registro.get("nombre_cientifico"))
        _campo("Presencia", _PRESENCIA_HUMANA.get(str(registro.get("presencia", "")).strip(), _formatear_valor(registro.get("presencia"))))
        _campo("Tipo de evidencia", _EVIDENCIA_HUMANA.get(str(registro.get("tipo_evidencia", "")).strip(), _formatear_valor(registro.get("tipo_evidencia"))))
        _campo("Observador", registro.get("nombre_observador"))

        observaciones = _limpiar_celda(registro.get("observaciones"))
        if observaciones:
            st.divider()
            st.caption("Observaciones")
            st.info(observaciones)

        st.divider()
        st.caption("Visita")
        _render_visita_madre(registro, id_visita)

        meteo = meteorologia_de_visita(tablas, id_visita)
        if not meteo.empty:
            st.divider()
            st.caption("Meteorología de la visita")
            _render_meteo(meteo)

        fotos = tablas.get("fotos", pd.DataFrame())
        fotos = filtrar_fotos_asociadas(fotos, id_visita, "mamiferos_puentes", registro.get("id_mamifero"))
        enlaces = enlaces_drive(fotos)
        if enlaces:
            st.divider()
            st.caption("Fotos asociadas")
            mostrar_enlaces_fotos(enlaces)


def _render_visita_madre(registro: pd.Series, id_visita: int | None) -> None:
    """Muestra datos de la visita asociada y botón de navegación."""
    _campo("ID visita", id_visita)
    _campo("Fecha", registro.get("fecha"))
    _campo("Lugar", registro.get("nombre_lugar_visita") or registro.get("nombre_lugar"))
    _campo("Observador", registro.get("nombre_observador"))
    _campo("Hora inicio", registro.get("hora_inicio"))
    _campo("Hora fin", registro.get("hora_fin"))
    if st.button("Ver visita", use_container_width=True, disabled=id_visita is None, key="mamiferos_ver_visita"):
        st.session_state["filtro_id_visita_visitas"] = id_visita
        st.session_state["pagina_activa"] = "Visitas"
        st.rerun()


def _render_meteo(meteo: pd.DataFrame) -> None:
    """Muestra meteorología de la visita con columnas renombradas."""
    nombres = {
        "hora": "Hora",
        "temperatura": "Temperatura",
        "nubosidad": "Nubosidad",
        "viento_direccion": "Dirección viento",
        "viento_intensidad": "Intensidad viento",
        "precipitacion": "Precipitación",
        "visibilidad": "Visibilidad",
    }
    cols = [c for c in nombres if c in meteo.columns]
    tabla_datos(meteo[cols].rename(columns=nombres), "Sin meteorología registrada para esta visita.")


def _campo(etiqueta: str, valor) -> None:
    """Muestra un campo de la ficha con etiqueta negrita y valor legible."""
    st.markdown(f"**{etiqueta}:** {_formatear_valor(valor)}")


def _formatear_valor(valor) -> str:
    """Convierte cualquier valor a texto limpio, sin tipos Python internos."""
    if valor is None:
        return "—"
    try:
        if pd.isna(valor):
            return "—"
    except (TypeError, ValueError):
        pass
    if isinstance(valor, time):
        return valor.strftime("%H:%M")
    if isinstance(valor, (pd.Timestamp, datetime.datetime)):
        return valor.strftime("%d/%m/%Y")
    if isinstance(valor, datetime.date):
        return valor.strftime("%d/%m/%Y")
    texto = str(valor).strip()
    if not texto or texto.lower() in {"none", "nan", "nat", "<na>"}:
        return "—"
    if len(texto) >= 10 and texto[4:5] == "-" and texto[7:8] == "-":
        try:
            dt = datetime.date.fromisoformat(texto[:10])
            return dt.strftime("%d/%m/%Y")
        except ValueError:
            pass
    texto = texto.replace("[SINTETICO_TEST]", "").strip()
    return texto or "—"


def _limpiar_celda(valor) -> str:
    """Convierte un valor de celda a texto limpio para la tabla."""
    if valor is None:
        return ""
    try:
        if pd.isna(valor):
            return ""
    except (TypeError, ValueError):
        pass
    texto = str(valor).replace("[SINTETICO_TEST]", "").strip()
    return "" if texto.lower() in {"none", "nan", "nat", "<na>"} else texto


def _grafico(df: pd.DataFrame, x: str, y: str, titulo: str) -> None:
    """Muestra gráfico o aviso."""
    chart = None if df.empty else grafico_barras(df, x, y)
    bloque_grafico(titulo, chart)


def _conteo(datos: pd.DataFrame, columna: str) -> pd.DataFrame:
    """Cuenta por columna."""
    if datos.empty or columna not in datos:
        return pd.DataFrame(columns=[columna, "total"])
    return datos.groupby(columna, dropna=False).size().reset_index(name="total")


def _diversidad_por_puente(datos: pd.DataFrame) -> pd.DataFrame:
    """Cuenta especies por puente."""
    if datos.empty or not {"nombre_lugar", "id_especie"}.issubset(datos.columns):
        return pd.DataFrame(columns=["nombre_lugar", "especies"])
    return datos.groupby("nombre_lugar")["id_especie"].nunique().reset_index(name="especies").sort_values("especies", ascending=False)


def _especies_por_puente(datos: pd.DataFrame) -> pd.DataFrame:
    """Cuenta registros por puente."""
    if datos.empty or "nombre_lugar" not in datos:
        return pd.DataFrame(columns=["nombre_lugar", "registros"])
    return datos.groupby("nombre_lugar").size().reset_index(name="registros")


def _rango_fechas(columna, datos: pd.DataFrame):
    """Selector de fechas."""
    fechas = pd.to_datetime(datos["fecha"], errors="coerce").dropna().dt.date
    if fechas.empty:
        return None, None
    rango = columna.date_input("Fecha", value=(fechas.min(), fechas.max()), key="mamiferos_fecha")
    return rango if isinstance(rango, tuple) and len(rango) == 2 else (None, None)


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
