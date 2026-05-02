"""Página de consulta Lindus."""

import datetime
from datetime import time

import pandas as pd
import streamlit as st

from dashboard.lib.consultas import (
    cargar_tablas_consulta,
    meteorologia_de_visita,
    observaciones_legibles,
    sumar_por,
)
from dashboard.lib.filtros import filtrar_fecha, filtrar_lugar, filtrar_rango_numerico, filtrar_valores, opciones_unicas
from dashboard.lib.fotos import enlaces_drive, filtrar_fotos_asociadas
from dashboard.lib.graficos import acumulado, grafico_barras, grafico_lineas
from dashboard.lib.ui import bloque_grafico, mostrar_enlaces_fotos, panel_filtros, rejilla_metricas, sin_datos, tabla_datos


@st.cache_data(ttl=120)
def _cargar_datos() -> dict[str, pd.DataFrame]:
    """Carga datos de consulta Lindus."""
    return cargar_tablas_consulta()


def render() -> None:
    """Renderiza la página Lindus."""
    try:
        tablas = _cargar_datos()
    except Exception as exc:
        st.warning(f"No se pudieron cargar datos: {exc}")
        return
    datos = observaciones_legibles("lindus", tablas)
    if datos.empty:
        sin_datos("Sin observaciones Lindus todavía.")
        return
    filtrados = _render_filtros(datos)
    _render_metricas(filtrados)
    _render_graficos(filtrados)
    _render_tabla_y_detalle(filtrados, tablas)


def _render_filtros(datos: pd.DataFrame) -> pd.DataFrame:
    """Dibuja filtros Lindus."""
    id_visita = _id_sesion("filtro_id_visita_lindus")
    if id_visita is not None:
        st.info(f"Filtro activo: visita #{id_visita}")
        if st.button("Limpiar filtro de visita", key="limpiar_filtro_lindus"):
            st.session_state.pop("filtro_id_visita_lindus", None)
            st.rerun()
        datos = datos[datos["id_visita"].astype("Int64") == id_visita]

    with panel_filtros():
        c1, c2, c3 = st.columns(3)
        desde, hasta = _rango_fechas(c1, datos)
        especies = c2.multiselect("Especie", opciones_unicas(datos, "nombre_comun"))
        comportamientos = c3.multiselect("Comportamiento", opciones_unicas(datos, "comportamiento"))
        c4, c5, c6 = st.columns(3)
        observadores = c4.multiselect("Observador", opciones_unicas(datos, "nombre_observador"))
        lugares = c5.multiselect("Lugar", opciones_unicas(datos, "nombre_lugar_visita"))
        hora_min, hora_max = _rango_horas(c6, datos)
        n_min, n_max = _rango_numero(datos)
    filtrados = filtrar_fecha(datos, desde=desde, hasta=hasta)
    filtrados = filtrar_valores(filtrados, "nombre_comun", especies)
    filtrados = filtrar_valores(filtrados, "comportamiento", comportamientos)
    filtrados = filtrar_valores(filtrados, "nombre_observador", observadores)
    filtrados = filtrar_lugar(filtrados, lugares)
    filtrados = filtrar_rango_numerico(filtrados, "numero", n_min, n_max)
    return _filtrar_hora(filtrados, hora_min, hora_max)


def _render_metricas(datos: pd.DataFrame) -> None:
    """Muestra métricas Lindus."""
    individuos = int(pd.to_numeric(datos.get("numero", pd.Series(dtype=int)), errors="coerce").fillna(0).sum())
    especies = datos["id_especie"].nunique() if "id_especie" in datos else 0
    dias = datos["fecha"].nunique() if "fecha" in datos else 0
    rejilla_metricas(
        [
            ("Observaciones", str(len(datos)) if len(datos) else "Sin datos", "Registros filtrados"),
            ("Individuos", str(individuos) if individuos else "Sin datos", "Suma de individuos"),
            ("Especies", str(especies) if especies else "Sin datos", "Especies filtradas"),
            ("Días", str(dias) if dias else "Sin datos", "Días con registros"),
        ]
    )


def _render_graficos(datos: pd.DataFrame) -> None:
    """Dibuja gráficos Lindus."""
    col1, col2 = st.columns(2)
    with col1:
        _grafico(_por_dia(datos), "fecha", "individuos", "Individuos por día", "lineas")
        _grafico(sumar_por(datos, "nombre_comun", "numero", "individuos"), "nombre_comun", "individuos", "Individuos por especie")
        _grafico(acumulado(_por_dia(datos), "fecha", "individuos"), "fecha", "acumulado", "Acumulado por temporada", "lineas")
    with col2:
        _grafico(sumar_por(datos, "comportamiento", "numero", "individuos"), "comportamiento", "individuos", "MIGRADOR / NORTE / LOCAL")
        _grafico(sumar_por(datos, "hora", "numero", "individuos"), "hora", "individuos", "Paso por hora", "lineas")
        top = sumar_por(datos, "nombre_comun", "numero", "individuos").sort_values("individuos", ascending=False).head(10)
        _grafico(top, "nombre_comun", "individuos", "Top especies")


def _render_tabla_y_detalle(datos: pd.DataFrame, tablas: dict[str, pd.DataFrame]) -> None:
    """Muestra tabla seleccionable a la izquierda y ficha de detalle a la derecha."""
    st.subheader("Observaciones")
    if datos.empty:
        sin_datos("Sin observaciones para los filtros.")
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
            key="lindus_tabla",
        )
        filas = estado.selection.rows
    with col_detalle:
        if not filas:
            st.info("Selecciona una observación en la tabla para ver el detalle.")
        else:
            _render_detalle(datos.iloc[filas[0]], tablas)


def _preparar_tabla(datos: pd.DataFrame) -> pd.DataFrame:
    """Prepara el DataFrame para mostrarlo como tabla legible."""
    mapa = {
        "fecha": "Fecha",
        "hora": "Hora",
        "nombre_comun": "Especie",
        "numero": "Nº",
        "comportamiento": "Comportamiento",
        "nombre_lugar_visita": "Lugar",
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
    if "Hora" in df.columns:
        df["Hora"] = df["Hora"].apply(_formatear_hora_tabla)
    for col in ("Especie", "Comportamiento", "Lugar", "Observador"):
        if col in df.columns:
            df[col] = df[col].apply(_limpiar_celda)
    return df.reset_index(drop=True)


def _formatear_hora_tabla(valor) -> str:
    """Formatea hora a HH:MM sin segundos ni tipos Python."""
    if valor is None:
        return ""
    try:
        if pd.isna(valor):
            return ""
    except (TypeError, ValueError):
        pass
    if isinstance(valor, time):
        return valor.strftime("%H:%M")
    texto = str(valor).strip()
    if len(texto) >= 5 and texto[2:3] == ":":
        return texto[:5]
    return texto


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


def _render_detalle(registro: pd.Series, tablas: dict[str, pd.DataFrame]) -> None:
    """Ficha de detalle de una observación Lindus, sin tipos Python crudos."""
    id_visita = _id_valor(registro.get("id_visita"))
    with st.container(border=True):
        st.subheader("Detalle de observación")
        _campo("Especie", registro.get("nombre_comun") or registro.get("nombre_cientifico"))
        _campo("Fecha", registro.get("fecha"))
        _campo("Hora", registro.get("hora"))
        _campo("Número", registro.get("numero"))
        _campo("Comportamiento", registro.get("comportamiento"))
        _campo("Lugar", registro.get("nombre_lugar_visita"))
        _campo("Observador", registro.get("nombre_observador"))
        _campo("Edad", registro.get("edad"))
        _campo("Sexo", registro.get("sexo"))
        _campo("Plumaje", registro.get("plumaje"))
        _campo("Observaciones", registro.get("observaciones"))

        st.divider()
        st.caption("Visita")
        _render_visita_madre(registro, id_visita)

        meteo = meteorologia_de_visita(tablas, id_visita)
        if not meteo.empty:
            st.divider()
            st.caption("Meteorología de la visita")
            if len(meteo) > 1:
                st.caption("Registros horarios de la misma visita.")
            _render_meteo(meteo)

        fotos = tablas.get("fotos", pd.DataFrame())
        fotos = filtrar_fotos_asociadas(fotos, id_visita, "lindus", registro.get("id_lindus"))
        enlaces = enlaces_drive(fotos)
        if enlaces:
            st.divider()
            st.caption("Fotos asociadas")
            mostrar_enlaces_fotos(enlaces)


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


def _render_visita_madre(registro: pd.Series, id_visita: int | None) -> None:
    """Muestra datos de la visita que contiene la observación."""
    _campo("ID visita", id_visita)
    _campo("Fecha", registro.get("fecha"))
    _campo("Lugar", registro.get("nombre_lugar_visita"))
    _campo("Observador", registro.get("nombre_observador"))
    _campo("Tipo de visita", _tipo_visita_humano(registro.get("tipo_visita")))
    if st.button("Ver visita", use_container_width=True, disabled=id_visita is None):
        st.session_state["filtro_id_visita_visitas"] = id_visita
        st.session_state["pagina_activa"] = "Visitas"
        st.rerun()


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
    return texto


def _tipo_visita_humano(valor) -> str:
    """Convierte tipo técnico de visita en etiqueta humana."""
    tipos = {
        "LINDUS": "Lindus",
        "CAJA_NIDO": "Cajas nido",
        "CEBO_AVISPON": "Cebos avispones",
        "NIDO_RAPAZ": "Nidos rapaces",
        "MAMIFEROS_PUENTES": "Mamíferos puentes",
        "IMPACTO_AMBIENTAL": "Impacto ambiental",
    }
    return tipos.get(str(valor), _formatear_valor(valor))


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


def _grafico(df: pd.DataFrame, x: str, y: str, titulo: str, tipo: str = "barras") -> None:
    """Muestra gráfico o aviso sin datos."""
    chart = None
    if not df.empty:
        chart = grafico_lineas(df, x, y) if tipo == "lineas" else grafico_barras(df, x, y)
    bloque_grafico(titulo, chart)


def _por_dia(datos: pd.DataFrame) -> pd.DataFrame:
    """Suma individuos por día."""
    if datos.empty or not {"fecha", "numero"}.issubset(datos.columns):
        return pd.DataFrame(columns=["fecha", "individuos"])
    return datos.groupby("fecha")["numero"].sum().reset_index(name="individuos")


def _rango_fechas(columna, datos: pd.DataFrame):
    """Selector de fechas."""
    if datos.empty or "fecha" not in datos:
        return None, None
    fechas = pd.to_datetime(datos["fecha"], errors="coerce").dropna().dt.date
    if fechas.empty:
        return None, None
    rango = columna.date_input("Fecha", value=(fechas.min(), fechas.max()), key="lindus_fecha")
    return rango if isinstance(rango, tuple) and len(rango) == 2 else (None, None)


def _rango_horas(columna, datos: pd.DataFrame) -> tuple[time | None, time | None]:
    """Selector de hora."""
    if datos.empty or "hora" not in datos:
        return None, None
    horas = pd.to_datetime(datos["hora"], errors="coerce").dropna().dt.time
    if horas.empty:
        return None, None
    hora_min, hora_max = min(horas), max(horas)
    if hora_min == hora_max:
        columna.caption(f"Hora: {hora_min}")
        return hora_min, hora_max
    return columna.slider("Hora", min_value=hora_min, max_value=hora_max, value=(hora_min, hora_max))


def _rango_numero(datos: pd.DataFrame) -> tuple[int, int]:
    """Selector de rango de número robusto."""
    if datos.empty or "numero" not in datos:
        return 0, 0
    numeros = pd.to_numeric(datos["numero"], errors="coerce").dropna()
    if numeros.empty:
        return 0, 0
    minimo, maximo = int(numeros.min()), int(numeros.max())
    if minimo == maximo:
        st.caption(f"Número de individuos: {minimo}")
        return minimo, maximo
    return st.slider("Número de individuos", min_value=minimo, max_value=maximo, value=(minimo, maximo))


def _filtrar_hora(datos: pd.DataFrame, hora_min: time | None, hora_max: time | None) -> pd.DataFrame:
    """Filtra por hora."""
    if datos.empty or "hora" not in datos or hora_min is None or hora_max is None:
        return datos
    horas = pd.to_datetime(datos["hora"], errors="coerce").dt.time
    return datos[(horas >= hora_min) & (horas <= hora_max)]
