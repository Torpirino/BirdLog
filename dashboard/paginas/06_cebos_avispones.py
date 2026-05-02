"""Página de consulta de cebos avispones."""

import datetime
from datetime import time

import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from dashboard.lib.consultas import cargar_tablas_consulta, meteorologia_de_visita, observaciones_legibles
from dashboard.lib.filtros import filtrar_fecha, filtrar_lugar, filtrar_rango_numerico, filtrar_valores, opciones_unicas
from dashboard.lib.fotos import enlaces_drive, filtrar_fotos_asociadas
from dashboard.lib.graficos import acumulado, grafico_barras, grafico_donut, grafico_lineas
from dashboard.lib.mapas import mapa_lugares
from dashboard.lib.ui import bloque_grafico, mostrar_enlaces_fotos, panel_filtros, rejilla_metricas, sin_datos, tabla_datos


CAPTURAS = ["vv", "crabro", "avispa_europea", "polilla", "mariposa", "otros"]

_ETIQUETAS_CAPTURAS = {
    "vv": "VV",
    "crabro": "Crabro",
    "avispa_europea": "Avispa europea",
    "polilla": "Polilla",
    "mariposa": "Mariposa",
    "otros": "Otros",
}


@st.cache_data(ttl=120)
def _cargar_datos() -> dict[str, pd.DataFrame]:
    """Carga datos de cebos."""
    return cargar_tablas_consulta()


def render() -> None:
    """Renderiza la página de cebos avispones."""
    try:
        tablas = _cargar_datos()
    except Exception as exc:
        st.warning(f"No se pudieron cargar datos: {exc}")
        return
    datos = observaciones_legibles("cebos_avispones", tablas)
    if datos.empty:
        sin_datos("Sin datos de cebos avispones todavía.")
        return
    datos = _normalizar_capturas(datos)
    filtrados = _render_filtros(datos)
    _render_metricas(filtrados)
    _render_graficos(filtrados)
    _render_mapa(filtrados)
    _render_tabla_y_detalle(filtrados, tablas)


def _render_filtros(datos: pd.DataFrame) -> pd.DataFrame:
    """Dibuja filtros de cebos."""
    id_visita = _id_sesion("filtro_id_visita_cebos_avispones")
    if id_visita is not None:
        st.info(f"Filtro activo: visita #{id_visita}")
        if st.button("Limpiar filtro de visita", key="limpiar_filtro_cebos"):
            st.session_state.pop("filtro_id_visita_cebos_avispones", None)
            st.rerun()
        datos = datos[datos["id_visita"].astype("Int64") == id_visita]

    with panel_filtros():
        c1, c2, c3 = st.columns(3)
        desde, hasta = _rango_fechas(c1, datos)
        lugares = c2.multiselect("Lugar / cebo", opciones_unicas(datos, "nombre_lugar"))
        municipios = c3.multiselect("Municipio", opciones_unicas(datos, "municipio"))
        vv_min, vv_max = _rango_vv(datos)
    filtrados = filtrar_fecha(datos, desde=desde, hasta=hasta)
    filtrados = filtrar_lugar(filtrados, lugares)
    filtrados = filtrar_valores(filtrados, "municipio", municipios)
    return filtrar_rango_numerico(filtrados, "vv", vv_min, vv_max)


def _render_metricas(datos: pd.DataFrame) -> None:
    """Muestra métricas de cebos."""
    vv = _suma(datos, "vv")
    crabro = _suma(datos, "crabro")
    otras = sum(_suma(datos, col) for col in ["avispa_europea", "polilla", "mariposa", "otros"])
    rejilla_metricas(
        [
            ("Revisiones", str(len(datos)) if len(datos) else "Sin datos", "Registros filtrados"),
            ("Total vv", str(vv) if vv else "Sin datos", "Vespa velutina"),
            ("Total crabro", str(crabro) if crabro else "Sin datos", "Vespa crabro"),
            ("Otras capturas", str(otras) if otras else "Sin datos", "Resto de capturas"),
        ]
    )


def _render_graficos(datos: pd.DataFrame) -> None:
    """Dibuja gráficos de cebos."""
    col1, col2 = st.columns(2)
    with col1:
        _grafico(_ranking_cebos(datos), "nombre_lugar", "vv", "Ranking de cebos")
        _grafico(_por_fecha(datos, "vv"), "fecha", "vv", "Evolución vv", "lineas")
        _grafico(acumulado(_por_fecha(datos, "vv"), "fecha", "vv"), "fecha", "acumulado", "Acumulado por periodo", "lineas")
    with col2:
        _grafico(_composicion(datos), "captura", "total", "Composición de capturas", "donut")
        _grafico(_por_fecha(datos, "crabro"), "fecha", "crabro", "Evolución crabro", "lineas")


def _render_mapa(datos: pd.DataFrame) -> None:
    """Muestra mapa de cebos."""
    st.subheader("Mapa de cebos")
    lugares = datos.drop_duplicates("id_lugar") if "id_lugar" in datos else pd.DataFrame()
    if lugares.empty:
        st.info("Sin coordenadas de cebos para los filtros.")
        return
    st_folium(mapa_lugares(lugares, "Cebos avispones"), use_container_width=True, height=460)


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
            key="cebos_tabla",
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
        "nombre_lugar": "Cebo / Lugar",
        "vv": "VV",
        "crabro": "Crabro",
        "avispa_europea": "Avispa europea",
        "polilla": "Polilla",
        "mariposa": "Mariposa",
        "otros": "Otros",
        "nombre_observador": "Observador",
    }
    cols = [c for c in mapa if c in datos.columns]
    df = datos[cols].copy().rename(columns=mapa)
    if "Fecha" in df.columns:
        df["Fecha"] = (
            pd.to_datetime(df["Fecha"], errors="coerce")
            .dt.strftime("%d/%m/%Y")
            .fillna("")
        )
    for col in ("Cebo / Lugar", "Observador"):
        if col in df.columns:
            df[col] = df[col].apply(_limpiar_celda)
    for col in ("VV", "Crabro", "Avispa europea", "Polilla", "Mariposa", "Otros"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").apply(
                lambda x: "" if pd.isna(x) else str(int(x))
            )
    return df.reset_index(drop=True)


def _render_detalle(registro: pd.Series, tablas: dict[str, pd.DataFrame]) -> None:
    """Ficha de detalle de una revisión de cebo avispón."""
    id_visita = _id_valor(registro.get("id_visita"))
    with st.container(border=True):
        st.subheader("Detalle de revisión")
        _campo("Cebo / Lugar", registro.get("nombre_lugar"))
        _campo("Fecha", registro.get("fecha"))
        _campo("Observador", registro.get("nombre_observador"))

        st.divider()
        st.caption("Capturas")
        for col, etiqueta in _ETIQUETAS_CAPTURAS.items():
            _campo(etiqueta, _entero_o_dash(registro.get(col)))

        total = sum(
            int(pd.to_numeric(registro.get(col, 0), errors="coerce") or 0)
            for col in CAPTURAS
        )
        st.markdown(f"**Total capturas:** {total}")

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
        fotos = filtrar_fotos_asociadas(fotos, id_visita, "cebos_avispones", registro.get("id_cebo"))
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
    if st.button("Ver visita", use_container_width=True, disabled=id_visita is None, key="cebos_ver_visita"):
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


def _entero_o_dash(valor) -> str:
    """Devuelve entero como string o '—' si es nulo/cero."""
    try:
        n = int(pd.to_numeric(valor, errors="coerce") or 0)
        return str(n) if n else "—"
    except (TypeError, ValueError):
        return "—"


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


def _grafico(df: pd.DataFrame, x: str, y: str, titulo: str, tipo: str = "barras") -> None:
    """Muestra gráfico o aviso."""
    chart = None
    if not df.empty:
        if tipo == "lineas":
            chart = grafico_lineas(df, x, y)
        elif tipo == "donut":
            chart = grafico_donut(df, x, y)
        else:
            chart = grafico_barras(df, x, y)
    bloque_grafico(titulo, chart)


def _normalizar_capturas(datos: pd.DataFrame) -> pd.DataFrame:
    """Convierte capturas a numérico."""
    copia = datos.copy()
    for columna in CAPTURAS:
        if columna in copia:
            copia[columna] = pd.to_numeric(copia[columna], errors="coerce").fillna(0)
    return copia


def _ranking_cebos(datos: pd.DataFrame) -> pd.DataFrame:
    """Suma vv por cebo."""
    if datos.empty or "nombre_lugar" not in datos:
        return pd.DataFrame(columns=["nombre_lugar", "vv"])
    return datos.groupby("nombre_lugar")["vv"].sum().reset_index().sort_values("vv", ascending=False)


def _por_fecha(datos: pd.DataFrame, columna: str) -> pd.DataFrame:
    """Suma capturas por fecha."""
    if datos.empty or columna not in datos or "fecha" not in datos:
        return pd.DataFrame(columns=["fecha", columna])
    return datos.groupby("fecha")[columna].sum().reset_index()


def _composicion(datos: pd.DataFrame) -> pd.DataFrame:
    """Calcula composición de capturas."""
    return pd.DataFrame({"captura": CAPTURAS, "total": [_suma(datos, col) for col in CAPTURAS]})


def _suma(datos: pd.DataFrame, columna: str) -> int:
    """Suma columna."""
    if datos.empty or columna not in datos:
        return 0
    return int(pd.to_numeric(datos[columna], errors="coerce").fillna(0).sum())


def _rango_fechas(columna, datos: pd.DataFrame):
    """Selector de fechas."""
    fechas = pd.to_datetime(datos["fecha"], errors="coerce").dropna().dt.date
    if fechas.empty:
        return None, None
    rango = columna.date_input("Fecha", value=(fechas.min(), fechas.max()), key="cebos_fecha")
    return rango if isinstance(rango, tuple) and len(rango) == 2 else (None, None)


def _rango_vv(datos: pd.DataFrame) -> tuple[int, int]:
    """Selector robusto para rango de vv."""
    minimo, maximo = int(datos["vv"].min()), int(datos["vv"].max())
    if minimo == maximo:
        st.caption(f"Rango vv: {minimo}")
        return minimo, maximo
    return st.slider("Rango vv", minimo, maximo, (minimo, maximo))


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
