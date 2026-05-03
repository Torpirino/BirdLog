"""App Streamlit de pipeline Plaud → Supabase."""

from __future__ import annotations

import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen
import webbrowser

import streamlit as st

RAIZ_PROYECTO = Path(__file__).resolve().parents[1]
if str(RAIZ_PROYECTO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROYECTO))

from app_pipeline.lib.enlaces import (
    LANZADOR_DASHBOARD,
    URL_CLAUDE_AI,
    URL_DASHBOARD,
)
from app_pipeline.lib.orquestador import comprobar_entorno, procesar_lote
from app_pipeline.lib.ui import (
    render_ayuda_acciones,
    render_estilos_pipeline,
    render_panel_lateral,
    render_registro_pipeline,
    render_resumen_global,
)

SCRIPT_DASHBOARD = RAIZ_PROYECTO / "scripts" / "abrir_dashboard.sh"


def _puerto_dashboard_activo() -> bool:
    """Comprueba si hay un proceso escuchando en el puerto del dashboard."""
    try:
        with socket.create_connection(("127.0.0.1", 8999), timeout=0.5):
            return True
    except OSError:
        return False


def _dashboard_responde() -> bool:
    """Comprueba que el dashboard responde por HTTP."""
    try:
        with urlopen(URL_DASHBOARD, timeout=0.8) as respuesta:
            return 200 <= respuesta.status < 400
    except (OSError, URLError):
        return False


def _esperar_dashboard(segundos: float = 8.0) -> bool:
    """Espera unos segundos a que el dashboard termine de arrancar."""
    fin = time.monotonic() + segundos
    while time.monotonic() < fin:
        if _dashboard_responde():
            return True
        time.sleep(0.5)
    return _dashboard_responde()


def _arrancar_dashboard() -> subprocess.Popen[bytes]:
    """Lanza el script del dashboard sin bloquear la app pipeline."""
    entorno = os.environ.copy()
    entorno["BIRDLOG_NO_ABRIR_NAVEGADOR"] = "1"
    return subprocess.Popen(
        ["bash", str(SCRIPT_DASHBOARD)],
        cwd=RAIZ_PROYECTO,
        env=entorno,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def abrir_dashboard_desde_pipeline() -> tuple[bool, str]:
    """Abre el dashboard o lo arranca antes si no está disponible."""
    if _dashboard_responde():
        webbrowser.open(URL_DASHBOARD)
        return True, "Dashboard abierto."

    if _puerto_dashboard_activo():
        if _esperar_dashboard():
            webbrowser.open(URL_DASHBOARD)
            return True, "Dashboard abierto."
        return False, (
            f"No se pudo abrir el dashboard. Puedes abrirlo manualmente "
            f"con el icono {LANZADOR_DASHBOARD}."
        )

    if not SCRIPT_DASHBOARD.exists():
        return False, (
            f"No se encontró el script de arranque. Puedes abrirlo manualmente "
            f"con el icono {LANZADOR_DASHBOARD}."
        )

    proceso = _arrancar_dashboard()
    if _esperar_dashboard():
        webbrowser.open(URL_DASHBOARD)
        return True, "Dashboard abierto."

    proceso.poll()
    return False, (
        f"No se pudo arrancar el dashboard. Puedes abrirlo manualmente "
        f"con el icono {LANZADOR_DASHBOARD}."
    )


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
        layout="wide",
    )
    render_estilos_pipeline()

    if "resultados" not in st.session_state:
        st.session_state["resultados"] = None

    estado_entorno = _estado_entorno_cacheado()
    panel_izquierdo, panel_derecho = st.columns([0.28, 0.72], gap="large")

    with panel_izquierdo:
        render_panel_lateral(estado_entorno)
        procesar = st.button(
            "▶ Procesar grabaciones de Plaud",
            disabled=not estado_entorno.ok,
            type="primary",
            use_container_width=True,
        )
        abrir_dashboard = st.button("📊 Abrir dashboard", use_container_width=True)
        st.link_button("💬 Abrir Claude.ai", url=URL_CLAUDE_AI, use_container_width=True)
        render_ayuda_acciones()

    with panel_derecho:
        st.markdown('<div style="height: 3rem;"></div>', unsafe_allow_html=True)
        if estado_entorno.ok and estado_entorno.entorno == "prod":
            st.warning(
                "⚠️ **ENTORNO PROD activo.** Cualquier archivo procesado "
                "modificará los datos reales.",
                icon="⚠️",
            )

        if abrir_dashboard:
            with st.spinner("Arrancando dashboard..."):
                abierto, mensaje = abrir_dashboard_desde_pipeline()
            if abierto:
                st.success(mensaje)
            else:
                st.error(mensaje)

        if procesar:
            st.session_state["_entorno_cache"] = None
            with st.status("Procesando grabaciones de Plaud…", expanded=True) as status:
                st.write("Buscando archivos .txt en Drive...")
                resultados = procesar_lote()
                st.session_state["resultados"] = resultados
                n_ok = sum(1 for r in resultados if r.estado == "OK")
                n_err = len(resultados) - n_ok
                st.write(f"Archivos encontrados: {len(resultados)}")
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

        render_resumen_global(st.session_state["resultados"])
        render_registro_pipeline(st.session_state["resultados"])


if __name__ == "__main__":
    main()
