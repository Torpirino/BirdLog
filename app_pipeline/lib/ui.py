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
            "": ICONO.get(r.estado, "?"),
            "Archivo": r.nombre,
            "Estado": ETIQUETA.get(r.estado, r.estado),
            "Etapa": r.etapa,
            "Movido a": r.txt_movido_a,
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


def _badge(texto_ok: str, texto_no: str, condicion: bool) -> None:
    """Muestra un badge verde u oscuro según la condición."""
    st.markdown(texto_ok if condicion else texto_no)
