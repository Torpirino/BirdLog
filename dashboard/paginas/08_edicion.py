"""Página de edición y catálogos."""

from datetime import date, time
from typing import Any

import pandas as pd
import streamlit as st

from dashboard.lib.consultas import ID_TABLA, cargar_tablas_consulta, etiqueta_registro, visitas_legibles
from dashboard.lib.edicion import (
    borrar_registro_seguro,
    campos_editables,
    campos_obligatorios,
    crear_registro,
    dependencias_registro,
    opciones_valor_cerrado,
    resumen_registro,
    tipo_campo,
    actualizar_registro,
    validar_registro,
    ORDEN_TABLAS,
)
from dashboard.lib.ui import bloque_info, encabezado_pagina, tabla_datos


ACCIONES = ["Ver", "Añadir", "Editar", "Borrar"]
TABLAS_CATALOGOS = ["especies", "observadores", "lugares"]


@st.cache_data(ttl=60)
def _cargar_datos() -> dict[str, pd.DataFrame]:
    """Carga tablas editables con caché corta."""
    return cargar_tablas_consulta()


def render() -> None:
    """Renderiza la página de edición."""
    encabezado_pagina(
        "Edición / Catálogos",
        "Altas, correcciones y borrado seguro con confirmación escrita.",
        "✏️",
    )
    bloque_info("Esta página modifica Supabase. Revisa cada acción antes de guardar o borrar.")
    try:
        tablas = _cargar_datos()
    except Exception as exc:
        st.warning(f"No se pudieron cargar datos: {exc}")
        return

    tabla, accion = _render_selectores()
    _render_datos_actuales(tabla, tablas)
    if accion == "Ver":
        return
    if accion == "Añadir":
        _render_alta(tabla, tablas)
    elif accion == "Editar":
        _render_edicion(tabla, tablas)
    elif accion == "Borrar":
        _render_borrado(tabla, tablas)


def _render_selectores() -> tuple[str, str]:
    """Dibuja selector de tabla y acción."""
    with st.container(border=True):
        col_tabla, col_accion = st.columns(2)
        tabla = col_tabla.selectbox(
            "Tabla",
            ORDEN_TABLAS,
            format_func=lambda nombre: f"Catálogo · {nombre}" if nombre in TABLAS_CATALOGOS else f"Datos · {nombre}",
        )
        accion = col_accion.radio("Acción", ACCIONES, horizontal=True)
    return tabla, accion


def _render_datos_actuales(tabla: str, tablas: dict[str, pd.DataFrame]) -> None:
    """Muestra registros existentes."""
    st.subheader("Registros existentes")
    df = tablas.get(tabla, pd.DataFrame())
    tabla_datos(_vista_tabla(tabla, df, tablas), "Sin registros todavía.")


def _render_alta(tabla: str, tablas: dict[str, pd.DataFrame]) -> None:
    """Formulario de alta."""
    st.subheader("Añadir registro")
    with st.form(f"alta_{tabla}", clear_on_submit=False):
        datos = _formulario(tabla, tablas, {})
        enviado = st.form_submit_button("Validar y guardar")
    if enviado:
        _guardar_alta(tabla, datos)


def _render_edicion(tabla: str, tablas: dict[str, pd.DataFrame]) -> None:
    """Formulario de edición."""
    df = tablas.get(tabla, pd.DataFrame())
    if df.empty:
        st.info("No hay registros para editar.")
        return
    registro = _selector_registro(tabla, df, tablas, "editar")
    if registro is None:
        return
    id_columna = ID_TABLA[tabla]
    st.subheader("Editar registro")
    with st.form(f"editar_{tabla}_{registro[id_columna]}", clear_on_submit=False):
        datos = _formulario(tabla, tablas, registro.to_dict())
        confirma = st.checkbox("Confirmo que quiero guardar estos cambios.")
        enviado = st.form_submit_button("Guardar cambios")
    if enviado:
        if not confirma:
            st.warning("Marca la confirmación antes de guardar.")
            return
        _guardar_edicion(tabla, int(registro[id_columna]), datos)


def _render_borrado(tabla: str, tablas: dict[str, pd.DataFrame]) -> None:
    """Flujo de borrado seguro."""
    df = tablas.get(tabla, pd.DataFrame())
    if df.empty:
        st.info("No hay registros para borrar.")
        return
    registro = _selector_registro(tabla, df, tablas, "borrar")
    if registro is None:
        return
    id_columna = ID_TABLA[tabla]
    id_registro = int(registro[id_columna])
    st.subheader("Borrado seguro")
    st.warning("Esta acción puede eliminar datos de Supabase. Revisa bien antes de continuar.")
    st.code(resumen_registro(tabla, registro.to_dict()))
    deps = dependencias_registro(tabla, id_registro, tablas)
    if deps:
        st.error("Este registro tiene dependencias cargadas. Supabase probablemente rechazará el borrado.")
        for dependencia in deps:
            st.caption(dependencia)
    st.info("Antes de borrar se intentará crear un backup CSV local en backups/ y una traza mínima local.")
    confirmacion = st.text_input("Escribe BORRAR para habilitar el botón final")
    if confirmacion == "BORRAR":
        if st.button("Borrar registro definitivamente", type="primary"):
            _ejecutar_borrado(tabla, id_registro)
    else:
        st.button("Borrar registro definitivamente", disabled=True)


def _formulario(tabla: str, tablas: dict[str, pd.DataFrame], valores: dict[str, Any]) -> dict[str, Any]:
    """Dibuja campos del formulario y devuelve payload."""
    datos = {}
    obligatorios = set(campos_obligatorios(tabla))
    for campo in campos_editables(tabla):
        etiqueta = f"{campo}{' *' if campo in obligatorios else ''}"
        datos[campo] = _widget_campo(tabla, campo, etiqueta, valores.get(campo), tablas)
    resultado = validar_registro(tabla, datos)
    if not resultado.ok:
        with st.expander("Validaciones pendientes", expanded=False):
            for error in resultado.errores:
                st.caption(error)
    return datos


def _widget_campo(tabla: str, campo: str, etiqueta: str, valor: Any, tablas: dict[str, pd.DataFrame]) -> Any:
    """Dibuja widget adecuado por campo."""
    opciones = opciones_valor_cerrado(tabla, campo)
    if opciones:
        return _select_cerrado(etiqueta, opciones, valor, campo)
    if campo in {"id_lugar", "id_especie", "id_observador", "id_visita"}:
        return _select_fk(campo, etiqueta, valor, tablas)
    tipo = tipo_campo(campo)
    if tipo == "date":
        return st.date_input(etiqueta, value=_valor_fecha(valor), key=f"{tabla}_{campo}").isoformat()
    if tipo == "time":
        valor_tiempo = _valor_hora(valor)
        return st.time_input(etiqueta, value=valor_tiempo, key=f"{tabla}_{campo}").strftime("%H:%M:%S") if valor_tiempo else st.text_input(etiqueta, value="", key=f"{tabla}_{campo}")
    if tipo == "bool":
        return st.checkbox(etiqueta, value=bool(valor) if valor is not None else False, key=f"{tabla}_{campo}")
    if tipo == "int":
        return _number_input(etiqueta, valor, True, f"{tabla}_{campo}")
    if tipo == "float":
        return _number_input(etiqueta, valor, False, f"{tabla}_{campo}")
    if campo in {"observaciones", "texto_revision", "comunicacion_personal", "descripcion"}:
        return st.text_area(etiqueta, value="" if valor is None else str(valor), key=f"{tabla}_{campo}")
    return st.text_input(etiqueta, value="" if valor is None else str(valor), key=f"{tabla}_{campo}")


def _select_cerrado(etiqueta: str, opciones: list[str], valor: Any, key: str) -> str | None:
    """Selector para valores cerrados."""
    opciones_ui = [""] + opciones
    actual = str(valor) if valor in opciones else ""
    return st.selectbox(etiqueta, opciones_ui, index=opciones_ui.index(actual), key=key) or None


def _select_fk(campo: str, etiqueta: str, valor: Any, tablas: dict[str, pd.DataFrame]) -> int | None:
    """Selector legible para claves foráneas."""
    tabla_fk = {"id_lugar": "lugares", "id_especie": "especies", "id_observador": "observadores", "id_visita": "visitas"}[campo]
    df = _df_fk(tabla_fk, tablas)
    if df.empty or campo not in df.columns:
        st.warning(f"No hay registros disponibles para {campo}.")
        return None
    ids = df[campo].dropna().astype(int).tolist()
    opciones = [None] + ids
    actual = int(valor) if pd.notna(valor) and valor != "" else None
    index = opciones.index(actual) if actual in opciones else 0
    return st.selectbox(etiqueta, opciones, index=index, format_func=lambda item: "" if item is None else _etiqueta_fk(tabla_fk, item, df), key=campo)


def _df_fk(tabla_fk: str, tablas: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Devuelve DataFrame de FK con columnas esperadas."""
    if tabla_fk == "visitas":
        return visitas_legibles(tablas)
    return tablas.get(tabla_fk, pd.DataFrame())


def _etiqueta_fk(tabla_fk: str, item: int, df: pd.DataFrame) -> str:
    """Etiqueta legible de FK."""
    id_columna = ID_TABLA[tabla_fk]
    fila = df[df[id_columna] == item]
    if fila.empty:
        return str(item)
    registro = fila.iloc[0]
    campos = {
        "lugares": ["nombre_lugar", "tipo_lugar"],
        "especies": ["nombre_cientifico", "nombre_comun"],
        "observadores": ["nombre_observador"],
        "visitas": ["fecha", "tipo_visita", "nombre_lugar"],
    }[tabla_fk]
    return etiqueta_registro(registro, id_columna, campos)


def _number_input(etiqueta: str, valor: Any, entero: bool, key: str) -> int | float | None:
    """Entrada numérica con opción de dejar vacío."""
    texto = "" if valor is None or pd.isna(valor) else str(valor)
    entrada = st.text_input(etiqueta, value=texto, key=key)
    if entrada.strip() == "":
        return None
    try:
        return int(entrada) if entero else float(entrada)
    except ValueError:
        st.error(f"{etiqueta} debe ser numérico.")
        return entrada


def _selector_registro(tabla: str, df: pd.DataFrame, tablas: dict[str, pd.DataFrame], accion: str) -> pd.Series | None:
    """Selector de registro existente."""
    id_columna = ID_TABLA[tabla]
    seleccion = st.selectbox(
        f"Registro a {accion}",
        df.index,
        format_func=lambda idx: _etiqueta_registro_tabla(tabla, df.loc[idx], tablas),
        key=f"{accion}_{tabla}",
    )
    return df.loc[seleccion] if seleccion is not None else None


def _etiqueta_registro_tabla(tabla: str, registro: pd.Series, tablas: dict[str, pd.DataFrame]) -> str:
    """Etiqueta por tabla para selector."""
    campos = {
        "especies": ["nombre_cientifico", "nombre_comun"],
        "observadores": ["nombre_observador"],
        "lugares": ["nombre_lugar", "tipo_lugar"],
        "visitas": ["fecha", "tipo_visita", "id_lugar"],
        "meteorologia": ["id_visita", "hora"],
        "lindus": ["id_visita", "hora", "id_especie"],
        "cajas_nido": ["id_visita", "id_lugar", "ocupada"],
        "nidos_rapaces": ["id_visita", "id_lugar"],
        "cebos_avispones": ["id_visita", "id_lugar", "vv"],
        "mamiferos_puentes": ["id_visita", "id_lugar", "id_especie"],
        "fotos": ["id_visita", "tabla_origen", "descripcion"],
    }.get(tabla, [])
    return etiqueta_registro(registro, ID_TABLA[tabla], campos)


def _vista_tabla(tabla: str, df: pd.DataFrame, tablas: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Prepara vista compacta de tabla."""
    if df.empty:
        return df
    columnas = [ID_TABLA[tabla]] + campos_editables(tabla)
    return df[[c for c in columnas if c in df.columns]].head(200)


def _guardar_alta(tabla: str, datos: dict[str, Any]) -> None:
    """Valida y crea registro."""
    resultado = validar_registro(tabla, datos)
    if not resultado.ok:
        for error in resultado.errores:
            st.error(error)
        return
    try:
        crear_registro(tabla, datos)
    except Exception as exc:
        st.error(f"No se pudo crear el registro: {exc}")
        return
    st.success("Registro creado correctamente.")
    _cargar_datos.clear()
    st.rerun()


def _guardar_edicion(tabla: str, id_registro: int, datos: dict[str, Any]) -> None:
    """Valida y actualiza registro."""
    resultado = validar_registro(tabla, datos)
    if not resultado.ok:
        for error in resultado.errores:
            st.error(error)
        return
    try:
        actualizar_registro(tabla, id_registro, datos)
    except Exception as exc:
        st.error(f"No se pudo actualizar el registro: {exc}")
        return
    st.success("Registro actualizado correctamente.")
    _cargar_datos.clear()
    st.rerun()


def _ejecutar_borrado(tabla: str, id_registro: int) -> None:
    """Ejecuta borrado seguro."""
    try:
        borrar_registro_seguro(tabla, id_registro, "BORRAR")
    except Exception as exc:
        st.error(f"No se pudo borrar el registro. Puede tener dependencias: {exc}")
        return
    st.success("Registro borrado correctamente.")
    _cargar_datos.clear()
    st.rerun()


def _valor_fecha(valor: Any) -> date:
    """Normaliza fecha para widget."""
    if valor is None or pd.isna(valor):
        return date.today()
    fecha = pd.to_datetime(valor, errors="coerce")
    return date.today() if pd.isna(fecha) else fecha.date()


def _valor_hora(valor: Any) -> time | None:
    """Normaliza hora para widget."""
    if valor is None or pd.isna(valor) or valor == "":
        return None
    hora = pd.to_datetime(str(valor), errors="coerce")
    return None if pd.isna(hora) else hora.time()
