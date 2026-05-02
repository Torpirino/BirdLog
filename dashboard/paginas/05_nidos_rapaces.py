"""Página de consulta de nidos de rapaces."""

import datetime
from datetime import time

import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from dashboard.lib.consultas import cargar_tablas_consulta, meteorologia_de_visita, observaciones_legibles
from dashboard.lib.filtros import filtrar_fecha, filtrar_lugar, filtrar_valores, opciones_unicas
from dashboard.lib.fotos import enlaces_drive, filtrar_fotos_asociadas
from dashboard.lib.mapas import mapa_lugares
from dashboard.lib.ui import mostrar_enlaces_fotos, panel_filtros, rejilla_metricas, sin_datos, tabla_datos


@st.cache_data(ttl=120)
def _cargar_datos() -> dict[str, pd.DataFrame]:
    """Carga datos de nidos rapaces."""
    return cargar_tablas_consulta()


def render() -> None:
    """Renderiza la página de nidos rapaces."""
    try:
        tablas = _cargar_datos()
    except Exception as exc:
        st.warning(f"No se pudieron cargar datos: {exc}")
        return
    datos = observaciones_legibles("nidos_rapaces", tablas)
    if datos.empty:
        sin_datos("Sin datos de nidos rapaces todavía.")
        return
    filtrados = _render_filtros(datos)
    _render_resumen(filtrados)
    _render_mapa(filtrados)
    _render_tabla_y_detalle(filtrados, tablas)


def _render_filtros(datos: pd.DataFrame) -> pd.DataFrame:
    """Dibuja filtros de rapaces."""
    id_visita = _id_sesion("filtro_id_visita_nidos_rapaces")
    if id_visita is not None:
        st.info(f"Filtro activo: visita #{id_visita}")
        if st.button("Limpiar filtro de visita", key="limpiar_filtro_rapaces"):
            st.session_state.pop("filtro_id_visita_nidos_rapaces", None)
            st.rerun()
        datos = datos[datos["id_visita"].astype("Int64") == id_visita]

    with panel_filtros():
        c1, c2, c3 = st.columns(3)
        desde, hasta = _rango_fechas(c1, datos)
        especies = c2.multiselect("Especie", opciones_unicas(datos, "nombre_comun"))
        lugares = c3.multiselect("Lugar / nido", opciones_unicas(datos, "nombre_lugar"))
    filtrados = filtrar_fecha(datos, desde=desde, hasta=hasta)
    filtrados = filtrar_valores(filtrados, "nombre_comun", especies)
    return filtrar_lugar(filtrados, lugares)


def _render_resumen(datos: pd.DataFrame) -> None:
    """Muestra métricas de rapaces."""
    nidos = datos["id_lugar"].nunique() if "id_lugar" in datos else 0
    especies = datos["id_especie"].nunique() if "id_especie" in datos else 0
    ultima = _ultima_fecha(datos)
    rejilla_metricas(
        [
            ("Revisiones", str(len(datos)) if len(datos) else "Sin datos", "Registros filtrados"),
            ("Nidos", str(nidos) if nidos else "Sin datos", "Lugares únicos"),
            ("Especies", str(especies) if especies else "Sin datos", "Especies revisadas"),
            ("Última revisión", ultima, "Fecha más reciente"),
        ]
    )


def _render_mapa(datos: pd.DataFrame) -> None:
    """Muestra mapa de nidos."""
    st.subheader("Mapa de nidos")
    lugares = datos.drop_duplicates("id_lugar") if "id_lugar" in datos else pd.DataFrame()
    if lugares.empty:
        st.info("Sin coordenadas de nidos para los filtros.")
        return
    st_folium(mapa_lugares(lugares, "Nidos rapaces"), use_container_width=True, height=460)
    columnas = ["nombre_lugar", "municipio", "utm_x", "utm_y"]
    tabla_datos(lugares[[c for c in columnas if c in lugares]], "Sin coordenadas para mostrar.")


def _render_tabla_y_detalle(datos: pd.DataFrame, tablas: dict[str, pd.DataFrame]) -> None:
    """Tabla seleccionable a la izquierda y ficha de detalle a la derecha."""
    st.subheader("Revisiones")
    if datos.empty:
        sin_datos("Sin revisiones para los filtros.")
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
            key="rapaces_tabla",
        )
        filas = estado.selection.rows
    with col_detalle:
        if not filas:
            st.info("Selecciona una revisión en la tabla para ver el detalle.")
        else:
            _render_detalle(datos.iloc[filas[0]], tablas)


def _preparar_tabla(datos: pd.DataFrame) -> pd.DataFrame:
    """Prepara DataFrame limpio para la tabla de revisiones."""
    mapa = {
        "fecha": "Fecha",
        "nombre_lugar": "Nido / Lugar",
        "nombre_comun": "Especie",
        "nombre_observador": "Observador",
        "comunicacion_personal": "Com. personal",
        "texto_revision": "Resumen",
    }
    cols = [c for c in mapa if c in datos.columns]
    df = datos[cols].copy().rename(columns=mapa)
    if "Fecha" in df.columns:
        df["Fecha"] = (
            pd.to_datetime(df["Fecha"], errors="coerce")
            .dt.strftime("%d/%m/%Y")
            .fillna("")
        )
    for col in ("Nido / Lugar", "Especie", "Observador", "Com. personal"):
        if col in df.columns:
            df[col] = df[col].apply(_limpiar_celda)
    if "Resumen" in df.columns:
        df["Resumen"] = df["Resumen"].apply(_truncar_texto)
    return df.reset_index(drop=True)


def _truncar_texto(valor, max_chars: int = 60) -> str:
    """Trunca texto largo para mostrarlo como resumen en la tabla."""
    texto = _limpiar_celda(valor)
    if not texto:
        return ""
    return texto[:max_chars] + "…" if len(texto) > max_chars else texto


def _render_detalle(registro: pd.Series, tablas: dict[str, pd.DataFrame]) -> None:
    """Ficha de detalle de una revisión de nido rapaz."""
    id_visita = _id_valor(registro.get("id_visita"))
    with st.container(border=True):
        st.subheader("Detalle de revisión")
        _campo("Nido / Lugar", registro.get("nombre_lugar"))
        _campo("Fecha", registro.get("fecha"))
        _campo("Especie", registro.get("nombre_comun") or registro.get("nombre_cientifico"))
        _campo("Observador", registro.get("nombre_observador"))
        _campo("Comunicación personal", registro.get("comunicacion_personal"))

        texto = _limpiar_celda(registro.get("texto_revision"))
        if texto:
            st.divider()
            st.caption("Texto de revisión")
            st.info(texto)

        st.divider()
        st.caption("Visita")
        _render_visita_madre(registro, id_visita)

        meteo = meteorologia_de_visita(tablas, id_visita)
        if not meteo.empty:
            st.divider()
            st.caption("Meteorología de la visita")
            _render_meteo(meteo)

        fotos = tablas.get("fotos", pd.DataFrame())
        fotos = filtrar_fotos_asociadas(fotos, id_visita, "nidos_rapaces", registro.get("id_nido_rapaz"))
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
    if st.button("Ver visita", use_container_width=True, disabled=id_visita is None, key="rapaces_ver_visita"):
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


def _rango_fechas(columna, datos: pd.DataFrame):
    """Selector de fechas."""
    fechas = pd.to_datetime(datos["fecha"], errors="coerce").dropna().dt.date
    if fechas.empty:
        return None, None
    rango = columna.date_input("Fecha", value=(fechas.min(), fechas.max()), key="rapaces_fecha")
    return rango if isinstance(rango, tuple) and len(rango) == 2 else (None, None)


def _ultima_fecha(datos: pd.DataFrame) -> str:
    """Última fecha legible."""
    if datos.empty or "fecha" not in datos:
        return "Sin datos"
    fecha = pd.to_datetime(datos["fecha"], errors="coerce").max()
    return "Sin datos" if pd.isna(fecha) else fecha.strftime("%d/%m/%Y")


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
