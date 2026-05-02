"""Página de consulta de cajas nido."""

import datetime
from datetime import time

import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from dashboard.lib.consultas import cargar_tablas_consulta, meteorologia_de_visita, observaciones_legibles, sumar_por
from dashboard.lib.filtros import filtrar_fecha, filtrar_lugar, filtrar_valores, opciones_unicas
from dashboard.lib.fotos import enlaces_drive, filtrar_fotos_asociadas
from dashboard.lib.graficos import grafico_barras, grafico_lineas
from dashboard.lib.mapas import mapa_lugares
from dashboard.lib.ui import bloque_grafico, mostrar_enlaces_fotos, panel_filtros, rejilla_metricas, sin_datos, tabla_datos


_CAMPOS_IB_PLUS = [
    ("orientacion_caja", "Orientación caja"),
    ("huevos_caliente_frio", "Huevos caliente/frío"),
    ("peso_pollos", "Peso pollos"),
    ("longitud_tarso", "Longitud tarso"),
    ("numero_anilla", "Número anilla"),
    ("distancia_rio", "Distancia río"),
    ("distancia_peatonal", "Distancia peatonal"),
    ("distancia_carretera", "Distancia carretera"),
    ("cobertura_vegetal", "Cobertura vegetal"),
    ("cobertura_arboles", "Cobertura árboles"),
    ("cobertura_matorral", "Cobertura matorral"),
    ("cobertura_pastizal", "Cobertura pastizal"),
]


@st.cache_data(ttl=120)
def _cargar_datos() -> dict[str, pd.DataFrame]:
    """Carga datos de cajas nido."""
    return cargar_tablas_consulta()


def render() -> None:
    """Renderiza la página de cajas nido."""
    try:
        tablas = _cargar_datos()
    except Exception as exc:
        st.warning(f"No se pudieron cargar datos: {exc}")
        return
    datos = observaciones_legibles("cajas_nido", tablas)
    if datos.empty:
        sin_datos("Sin datos de cajas nido todavía.")
        return
    filtrados = _render_filtros(datos)
    _render_metricas(filtrados)
    _render_graficos(filtrados)
    _render_mapa(filtrados)
    _render_tabla_y_detalle(filtrados, tablas)


def _render_filtros(datos: pd.DataFrame) -> pd.DataFrame:
    """Dibuja filtros de cajas."""
    id_visita = _id_sesion("filtro_id_visita_cajas_nido")
    if id_visita is not None:
        st.info(f"Filtro activo: visita #{id_visita}")
        if st.button("Limpiar filtro de visita", key="limpiar_filtro_cajas"):
            st.session_state.pop("filtro_id_visita_cajas_nido", None)
            st.rerun()
        datos = datos[datos["id_visita"].astype("Int64") == id_visita]

    with panel_filtros():
        c1, c2, c3 = st.columns(3)
        desde, hasta = _rango_fechas(c1, datos)
        lugares = c2.multiselect("Lugar / caja", opciones_unicas(datos, "nombre_lugar"))
        especies = c3.multiselect("Especie", opciones_unicas(datos, "nombre_comun"))
        c4, c5, c6 = st.columns(3)
        ecosistemas = c4.multiselect("Ecosistema", opciones_unicas(datos, "ecosistema"))
        estados = c5.multiselect("Estado nido", opciones_unicas(datos, "estado_nido"))
        ocupada = c6.selectbox("Ocupada", ["Todas", "Sí", "No"])
    filtrados = filtrar_fecha(datos, desde=desde, hasta=hasta)
    filtrados = filtrar_lugar(filtrados, lugares)
    filtrados = filtrar_valores(filtrados, "nombre_comun", especies)
    filtrados = filtrar_valores(filtrados, "ecosistema", ecosistemas)
    filtrados = filtrar_valores(filtrados, "estado_nido", estados)
    if ocupada != "Todas" and "ocupada" in filtrados:
        filtrados = filtrados[filtrados["ocupada"].astype(bool) == (ocupada == "Sí")]
    return filtrados


def _render_metricas(datos: pd.DataFrame) -> None:
    """Muestra métricas de cajas."""
    ocupadas = int(datos["ocupada"].fillna(False).astype(bool).sum()) if "ocupada" in datos else 0
    total = len(datos)
    porcentaje = f"{(ocupadas / total * 100):.0f}%" if total else "Sin datos"
    huevos = _suma(datos, "numero_huevos")
    pollos = _suma(datos, "numero_pollos")
    rejilla_metricas(
        [
            ("Cajas revisadas", str(total) if total else "Sin datos", "Revisiones filtradas"),
            ("Cajas ocupadas", str(ocupadas) if ocupadas else "Sin datos", "Revisiones ocupadas"),
            ("Ocupación", porcentaje, "Porcentaje de revisiones ocupadas"),
            ("Huevos / pollos", f"{huevos} / {pollos}", "Totales filtrados"),
        ]
    )


def _render_graficos(datos: pd.DataFrame) -> None:
    """Dibuja gráficos de cajas."""
    col1, col2 = st.columns(2)
    with col1:
        _grafico(_ocupacion_por(datos, "ecosistema"), "ecosistema", "ocupadas", "Ocupación por ecosistema")
        _grafico(sumar_por(datos, "nombre_lugar", "numero_huevos", "huevos"), "nombre_lugar", "huevos", "Huevos por caja")
    with col2:
        _grafico(_conteo(datos, "estado_nido"), "estado_nido", "total", "Estado del nido")
        _grafico(_evolucion(datos), "fecha", "revisiones", "Evolución por fecha", "lineas")
        _grafico(sumar_por(datos, "nombre_lugar", "numero_pollos", "pollos"), "nombre_lugar", "pollos", "Pollos por caja")


def _render_mapa(datos: pd.DataFrame) -> None:
    """Muestra mapa de cajas."""
    st.subheader("Mapa de cajas")
    lugares = datos.drop_duplicates("id_lugar") if "id_lugar" in datos else pd.DataFrame()
    if lugares.empty:
        st.info("Sin coordenadas de cajas para los filtros.")
        return
    st_folium(mapa_lugares(lugares, "Cajas nido"), use_container_width=True, height=460)


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
            key="cajas_tabla",
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
        "nombre_lugar": "Caja / Lugar",
        "nombre_comun": "Especie",
        "ecosistema": "Ecosistema",
        "estado_nido": "Estado nido",
        "ocupada": "Ocupada",
        "numero_huevos": "Huevos",
        "numero_pollos": "Pollos",
    }
    cols = [c for c in mapa if c in datos.columns]
    df = datos[cols].copy().rename(columns=mapa)
    if "Fecha" in df.columns:
        df["Fecha"] = (
            pd.to_datetime(df["Fecha"], errors="coerce")
            .dt.strftime("%d/%m/%Y")
            .fillna("")
        )
    if "Ocupada" in df.columns:
        df["Ocupada"] = df["Ocupada"].apply(_formatear_bool)
    for col in ("Caja / Lugar", "Especie", "Ecosistema", "Estado nido"):
        if col in df.columns:
            df[col] = df[col].apply(_limpiar_celda)
    for col in ("Huevos", "Pollos"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").apply(
                lambda x: "" if pd.isna(x) else str(int(x))
            )
    return df.reset_index(drop=True)


def _render_detalle(registro: pd.Series, tablas: dict[str, pd.DataFrame]) -> None:
    """Ficha de detalle de una revisión de caja nido."""
    id_visita = _id_valor(registro.get("id_visita"))
    with st.container(border=True):
        st.subheader("Detalle de revisión")
        _campo("Caja / Lugar", registro.get("nombre_lugar"))
        _campo("Fecha", registro.get("fecha"))
        _campo("Especie", registro.get("nombre_comun") or registro.get("nombre_cientifico"))
        _campo("Ecosistema", registro.get("ecosistema"))
        _campo("Estado del nido", registro.get("estado_nido"))
        _campo("Ocupada", _formatear_bool(registro.get("ocupada")) or "—")
        _campo("Huevos", registro.get("numero_huevos"))
        _campo("Pollos", registro.get("numero_pollos"))
        _campo("Especie de árbol", registro.get("especie_arbol"))
        _campo("Observaciones", registro.get("observaciones"))

        _render_campos_ib_plus(registro)

        st.divider()
        st.caption("Visita")
        _render_visita_madre(registro, id_visita)

        meteo = meteorologia_de_visita(tablas, id_visita)
        if not meteo.empty:
            st.divider()
            st.caption("Meteorología de la visita")
            _render_meteo(meteo)

        fotos = tablas.get("fotos", pd.DataFrame())
        fotos = filtrar_fotos_asociadas(fotos, id_visita, "cajas_nido", registro.get("id_cajanido"))
        enlaces = enlaces_drive(fotos)
        if enlaces:
            st.divider()
            st.caption("Fotos asociadas")
            mostrar_enlaces_fotos(enlaces)


def _render_campos_ib_plus(registro: pd.Series) -> None:
    """Muestra campos IB+ solo si tienen valor real."""
    campos_con_valor = [
        (etiqueta, registro.get(campo))
        for campo, etiqueta in _CAMPOS_IB_PLUS
        if _tiene_valor(registro.get(campo))
    ]
    if campos_con_valor:
        st.divider()
        st.caption("Campos IB+")
        for etiqueta, valor in campos_con_valor:
            _campo(etiqueta, valor)


def _render_visita_madre(registro: pd.Series, id_visita: int | None) -> None:
    """Muestra datos de la visita asociada y botón de navegación."""
    _campo("ID visita", id_visita)
    _campo("Fecha", registro.get("fecha"))
    _campo("Lugar", registro.get("nombre_lugar_visita") or registro.get("nombre_lugar"))
    _campo("Observador", registro.get("nombre_observador"))
    _campo("Hora inicio", registro.get("hora_inicio"))
    _campo("Hora fin", registro.get("hora_fin"))
    if st.button("Ver visita", use_container_width=True, disabled=id_visita is None, key="cajas_ver_visita"):
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
    return texto


def _formatear_bool(valor) -> str:
    """Convierte booleano a Sí / No / vacío."""
    if valor is None:
        return ""
    try:
        if pd.isna(valor):
            return ""
    except (TypeError, ValueError):
        pass
    try:
        return "Sí" if bool(valor) else "No"
    except (TypeError, ValueError):
        return ""


def _tiene_valor(valor) -> bool:
    """True si el valor es real (no nulo ni vacío)."""
    if valor is None:
        return False
    try:
        if pd.isna(valor):
            return False
    except (TypeError, ValueError):
        pass
    return bool(str(valor).strip()) and str(valor).lower() not in {"none", "nan", "nat", "<na>"}


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
        chart = grafico_lineas(df, x, y) if tipo == "lineas" else grafico_barras(df, x, y)
    bloque_grafico(titulo, chart)


def _rango_fechas(columna, datos: pd.DataFrame):
    """Selector de fechas."""
    fechas = pd.to_datetime(datos["fecha"], errors="coerce").dropna().dt.date
    if fechas.empty:
        return None, None
    rango = columna.date_input("Fecha", value=(fechas.min(), fechas.max()), key="cajas_fecha")
    return rango if isinstance(rango, tuple) and len(rango) == 2 else (None, None)


def _suma(datos: pd.DataFrame, columna: str) -> int:
    """Suma columna numérica."""
    if datos.empty or columna not in datos:
        return 0
    return int(pd.to_numeric(datos[columna], errors="coerce").fillna(0).sum())


def _ocupacion_por(datos: pd.DataFrame, columna: str) -> pd.DataFrame:
    """Cuenta ocupadas por grupo."""
    if datos.empty or columna not in datos or "ocupada" not in datos:
        return pd.DataFrame(columns=[columna, "ocupadas"])
    copia = datos.copy()
    copia["ocupadas"] = copia["ocupada"].fillna(False).astype(bool).astype(int)
    return copia.groupby(columna)["ocupadas"].sum().reset_index()


def _conteo(datos: pd.DataFrame, columna: str) -> pd.DataFrame:
    """Cuenta filas por columna."""
    if datos.empty or columna not in datos:
        return pd.DataFrame(columns=[columna, "total"])
    return datos.groupby(columna).size().reset_index(name="total")


def _evolucion(datos: pd.DataFrame) -> pd.DataFrame:
    """Cuenta revisiones por fecha."""
    if datos.empty or "fecha" not in datos:
        return pd.DataFrame(columns=["fecha", "revisiones"])
    return datos.groupby("fecha").size().reset_index(name="revisiones")


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
