"""Componentes visuales para la app pipeline."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app_pipeline.lib.estados import (
    ESTADO_INCOMPLETO,
    ESTADO_OK,
    ETIQUETA,
    ICONO,
    EstadoEntorno,
    ResultadoArchivo,
)


def render_cabecera(estado: EstadoEntorno) -> None:
    """Muestra título, indicador de entorno y mensajes de error."""
    st.title("🦅 BirdLog — Pipeline Plaud")
    st.caption("Procesa las grabaciones del Plaud, insértalas en Supabase y crea el backup.")

    if estado.ok:
        col1, col2, col3 = st.columns(3)
        col1.success(f"🌱 Entorno: **{estado.entorno}**")
        col2.success("📂 Drive accesible")
        col3.success("🗄️ Supabase conectado")
    else:
        if estado.entorno == "prod":
            st.warning(
                "⚠️ **Atención**: estás en el entorno de **producción**. "
                "Cualquier procesado modificará los datos reales."
            )
        _mensaje_error_entorno(estado)
        _ayuda_entorno(estado)


def render_estilos_pipeline() -> None:
    """Ajusta espacios y legibilidad para la pantalla operativa."""
    st.markdown(
        """
        <style>
            .block-container {
                max-width: 1500px;
                padding-top: 1.25rem;
                padding-bottom: 2rem;
            }
            .stTextArea textarea {
                background: #101815;
                border: 1px solid rgba(112, 175, 132, 0.35);
                font-family: "Ubuntu Mono", "SFMono-Regular", Consolas, monospace;
                font-size: 0.92rem;
                line-height: 1.45;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_panel_lateral(estado: EstadoEntorno) -> None:
    """Muestra identidad, estado y ayudas breves en el panel izquierdo."""
    st.markdown("## 🦅 BirdLog")
    st.markdown("### Pipeline Plaud")
    st.caption("Procesa las grabaciones de Plaud e insértalas en Supabase.")

    st.markdown("**Estado del sistema**")
    _estado_compacto(estado)

    if not estado.ok:
        _mensaje_error_entorno(estado)
        _ayuda_entorno(estado)

    st.markdown("**Acciones**")


def _estado_compacto(estado: EstadoEntorno) -> None:
    """Muestra el estado en formato vertical y compacto."""
    if estado.entorno == "prod":
        st.warning("Entorno: **prod**", icon="⚠️")
    elif estado.entorno == "?":
        st.error("Entorno: sin configurar", icon="⚙️")
    else:
        st.success(f"Entorno: **{estado.entorno}**", icon="🌱")

    if estado.drive_ok:
        st.success("Drive accesible", icon="📂")
    else:
        st.error("Drive no accesible", icon="📂")

    if estado.supabase_ok:
        st.success("Supabase conectado", icon="🗄️")
    else:
        st.error("Supabase sin conexión", icon="🗄️")


def render_ayuda_acciones() -> None:
    """Muestra ayuda breve bajo los botones del panel izquierdo."""
    st.caption("Dashboard: se abre automáticamente si no está arrancado.")
    st.caption("Claude.ai: usa el proyecto BirdLog para consultar dudas.")


def render_resumen_global(resultados: list[ResultadoArchivo] | None) -> None:
    """Muestra el resumen global del último procesamiento."""
    if resultados is None:
        st.info("Aún no has procesado ninguna grabación en esta sesión.", icon="ℹ️")
        return

    if not resultados:
        st.info("No había grabaciones nuevas en Drive.", icon="📭")
        return

    n_ok = sum(1 for resultado in resultados if resultado.estado == ESTADO_OK)
    n_error = sum(1 for resultado in resultados if resultado.estado == ESTADO_ERROR)
    n_incompleto = sum(1 for resultado in resultados if resultado.estado == ESTADO_INCOMPLETO)

    if n_error:
        st.error(_texto_resumen(n_ok, n_error, n_incompleto), icon="🔴")
    elif n_incompleto:
        st.warning(_texto_resumen(n_ok, n_error, n_incompleto), icon="🟡")
    else:
        st.success(_texto_resumen(n_ok, n_error, n_incompleto), icon="🟢")


def _texto_resumen(n_ok: int, n_error: int, n_incompleto: int) -> str:
    """Construye una frase corta de resumen global."""
    partes = []
    if n_ok:
        etiqueta = (
            "grabación procesada correctamente"
            if n_ok == 1
            else "grabaciones procesadas correctamente"
        )
        partes.append(f"{n_ok} {etiqueta}")
    if n_error:
        etiqueta = "error" if n_error == 1 else "errores"
        partes.append(f"{n_error} {etiqueta}")
    if n_incompleto:
        etiqueta = "incompleto" if n_incompleto == 1 else "incompletos"
        partes.append(f"{n_incompleto} {etiqueta}")
    return ". ".join(partes) + "."


def _mensaje_error_entorno(estado: EstadoEntorno) -> None:
    """Muestra un mensaje de error principal breve y legible."""
    if estado.entorno == "?":
        st.error("⚙️ Falta configuración. La app no puede arrancar.")
    elif not estado.drive_ok:
        st.error("📂 No se pudo acceder a Google Drive.")
    elif not estado.supabase_ok:
        st.error("🗄️ No se pudo conectar con Supabase.")
    else:
        st.error(estado.mensaje)


def _ayuda_entorno(estado: EstadoEntorno) -> None:
    """Muestra ayuda de resolución según qué falla, con detalles opcionales."""
    if estado.entorno == "?":
        with st.expander("¿Qué tengo que hacer?"):
            st.markdown(
                "El archivo de configuración `.env` no está completo o no se puede leer.\n\n"
                "**Pasos:**\n"
                "1. Comprueba que el archivo `.env` existe en la carpeta del proyecto.\n"
                "2. Verifica que todos los campos tienen un valor rellenado.\n"
                "3. Si no sabes cómo configurarlo, consulta a Claude.ai."
            )
            st.caption(f"Detalle técnico: {estado.mensaje}")
    elif not estado.drive_ok:
        with st.expander("¿Qué tengo que hacer?"):
            st.markdown(
                "**Causas más frecuentes:**\n"
                "- El archivo de credenciales de Google no existe o la ruta en `.env` "
                "es incorrecta (`GOOGLE_CREDENTIALS_PATH`).\n"
                "- Las carpetas de Drive no están compartidas con la cuenta de servicio "
                "`birdlog-drive`.\n"
                "- Problema de conexión a internet.\n\n"
                "Si el problema persiste, consulta a Claude.ai con el mensaje de detalle."
            )
            st.caption(f"Detalle técnico: {estado.mensaje}")
    elif not estado.supabase_ok:
        with st.expander("¿Qué tengo que hacer?"):
            st.markdown(
                "1. Entra en [supabase.com](https://supabase.com) y comprueba que el proyecto "
                "está activo (no pausado).\n"
                "2. Si está pausado, pulsa **Restore** y espera unos segundos.\n"
                "3. Vuelve a cargar esta página."
            )


def render_resultados(resultados: list[ResultadoArchivo]) -> None:
    """Muestra tabla resumen y tarjetas detalladas de cada resultado."""
    if not resultados:
        st.info("No había grabaciones nuevas en Drive (carpeta 01_entrada vacía).", icon="📭")
        return

    st.subheader("Resultados del procesado")
    _tabla_resumen(resultados)
    st.divider()
    for resultado in resultados:
        _tarjeta_resultado(resultado)


def _tabla_resumen(resultados: list[ResultadoArchivo]) -> None:
    """Muestra tabla compacta con el estado de cada archivo."""
    filas = [
        {
            "archivo": r.nombre,
            "estado": f"{ICONO.get(r.estado, '?')} {ETIQUETA.get(r.estado, r.estado)}",
            "id_visita": "-",
            "backup": "sí" if r.backup_creado else "no",
            "movimiento_drive": r.txt_movido_a,
            "mensaje": r.mensaje,
        }
        for r in resultados
    ]
    st.dataframe(pd.DataFrame(filas), hide_index=True, use_container_width=True)


def _tarjeta_resultado(r: ResultadoArchivo) -> None:
    """Renderiza una tarjeta detallada expandible por archivo."""
    icono = ICONO.get(r.estado, "?")
    etiqueta = ETIQUETA.get(r.estado, r.estado)

    with st.expander(f"{icono}  {r.nombre}", expanded=(r.estado != ESTADO_OK)):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Estado:** {etiqueta}")
            st.markdown(f"**Etapa final:** {r.etapa}")
            st.markdown(f"**📁 .txt movido a:** `{r.txt_movido_a}`")
        with col2:
            _badge("✅ Insertado en Supabase", "❌ No insertado en Supabase", r.insertado_supabase)
            _badge("✅ Backup creado", "❌ Sin backup", r.backup_creado)
            if r.insertado_supabase and not r.backup_creado:
                st.warning("Backup pendiente. El registro sí está en Supabase.", icon="⚠️")

        if r.estado != ESTADO_OK:
            st.markdown("---")
            st.markdown("**Mensaje:**")
            st.code(r.mensaje, language=None)
            if r.estado == ESTADO_INCOMPLETO:
                st.info(
                    "Da de alta el dato que falta en Supabase (tablas `especies`, `lugares` "
                    "u `observadores`) y añade el nombre al vocabulario del Plaud. "
                    "Luego mueve el archivo de `03_errores` a `01_entrada` y vuelve a procesar.",
                    icon="ℹ️",
                )

        if r.estado == ESTADO_OK:
            st.success(r.mensaje)


def render_registro_pipeline(resultados: list[ResultadoArchivo] | None) -> None:
    """Muestra un registro amplio y legible del último procesado."""
    st.subheader("Registro de procesamiento")

    if resultados is None:
        st.text_area(
            "Mensajes del pipeline",
            value="Aún no has procesado ninguna grabación en esta sesión.",
            height=500,
            disabled=True,
            label_visibility="collapsed",
        )
        return

    mensajes = _mensajes_registro(resultados)
    st.text_area(
        "Mensajes del pipeline",
        value="\n".join(mensajes),
        height=500,
        disabled=True,
        label_visibility="collapsed",
    )

    if resultados:
        st.markdown("**Resumen por archivo**")
        _tabla_resumen(resultados)
        st.markdown("**Detalle por archivo**")
        for resultado in resultados:
            _tarjeta_resultado(resultado)


def _mensajes_registro(resultados: list[ResultadoArchivo]) -> list[str]:
    """Construye mensajes de usuario a partir del resultado final."""
    mensajes = ["Buscando archivos .txt en Drive..."]
    if not resultados:
        return [
            *mensajes,
            "Archivos encontrados: 0",
            "No había grabaciones nuevas en la carpeta 01_entrada.",
            "Resumen final: nada que procesar.",
        ]

    mensajes.append(f"Archivos encontrados: {len(resultados)}")
    for resultado in resultados:
        mensajes.extend(_mensajes_archivo(resultado))

    n_ok = sum(1 for resultado in resultados if resultado.estado == ESTADO_OK)
    n_error = len(resultados) - n_ok
    mensajes.append(f"Resumen final: {n_ok} correcto(s), {n_error} con error o incompleto(s).")
    return mensajes


def _mensajes_archivo(resultado: ResultadoArchivo) -> list[str]:
    """Construye mensajes claros para un archivo."""
    estado = ETIQUETA.get(resultado.estado, resultado.estado)
    insertado = "insertado en Supabase" if resultado.insertado_supabase else "no insertado en Supabase"
    backup = "backup creado" if resultado.backup_creado else "sin backup"
    movido = f"movido a {resultado.txt_movido_a}" if resultado.txt_movido_a != "-" else "sin movimiento de carpeta"
    mensajes = [
        "",
        f"Archivo: {resultado.nombre}",
        f"- Estado: {estado}",
        f"- Etapa final: {resultado.etapa}",
        f"- Supabase: {insertado}",
        f"- Backup: {backup}",
        f"- Drive: {movido}",
    ]
    if resultado.estado == ESTADO_OK:
        mensajes.append(f"- Mensaje: {resultado.mensaje}")
    else:
        mensajes.append("- Mensaje: revisa el detalle desplegable de este archivo.")
    return mensajes


def _badge(texto_ok: str, texto_no: str, condicion: bool) -> None:
    """Muestra un badge verde u oscuro según la condición."""
    st.markdown(texto_ok if condicion else texto_no)
