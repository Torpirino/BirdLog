"""App Streamlit de pipeline Plaud → Supabase."""

from __future__ import annotations

import time

import streamlit as st

from app_pipeline.lib.enlaces import COMANDO_DASHBOARD, URL_CLAUDE_AI, URL_DASHBOARD
from app_pipeline.lib.orquestador import comprobar_entorno, procesar_lote
from app_pipeline.lib.ui import render_cabecera, render_resultados


def _estado_entorno_cacheado() -> object:
    """Devuelve el estado del entorno con caché de 30 s en session_state."""
    ahora = time.time()
    cache = st.session_state.get("_entorno_cache")
    if cache and ahora - cache["ts"] < 30:
        return cache["estado"]
    estado = comprobar_entorno()
    st.session_state["_entorno_cache"] = {"ts": ahora, "estado": estado}
    return estado


def main() -> None:
    st.set_page_config(
        page_title="BirdLog — Pipeline Plaud",
        page_icon="🦅",
        layout="centered",
    )

    if "resultados" not in st.session_state:
        st.session_state["resultados"] = None

    estado_entorno = _estado_entorno_cacheado()
    render_cabecera(estado_entorno)

    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        procesar = st.button(
            "▶ Procesar grabaciones de Plaud",
            disabled=not estado_entorno.ok,
            type="primary",
            use_container_width=True,
        )
    with col2:
        st.link_button("📊 Abrir dashboard", url=URL_DASHBOARD, use_container_width=True)
    with col3:
        st.link_button("💬 Abrir Claude.ai", url=URL_CLAUDE_AI, use_container_width=True)

    st.caption(f"Dashboard: `{COMANDO_DASHBOARD}`")
    st.caption(
        "Claude.ai — Usa el proyecto BirdLog en Claude para consultar documentación, "
        "decisiones y dudas del sistema. Claude no accede a Supabase directamente."
    )

    if estado_entorno.ok and estado_entorno.entorno == "prod":
        st.warning(
            "⚠️ **ENTORNO PROD activo.** Cualquier archivo procesado modificará los datos reales.",
            icon="⚠️",
        )

    st.divider()

    if procesar:
        st.session_state["_entorno_cache"] = None
        with st.status("Procesando grabaciones de Plaud…", expanded=True) as status:
            resultados = procesar_lote()
            st.session_state["resultados"] = resultados
            n_ok = sum(1 for r in resultados if r.estado == "OK")
            n_err = len(resultados) - n_ok
            if not resultados:
                status.update(
                    label="No había grabaciones nuevas en Drive.",
                    state="complete",
                )
            elif n_err == 0:
                status.update(
                    label=f"✅ {n_ok} grabación(es) procesada(s) correctamente.",
                    state="complete",
                )
            else:
                status.update(
                    label=f"⚠️ {n_ok} OK · {n_err} con error o incompleto.",
                    state="error",
                )

    if st.session_state["resultados"] is None:
        st.info("Aún no has procesado ninguna grabación en esta sesión.", icon="💤")
    else:
        render_resultados(st.session_state["resultados"])


main()
