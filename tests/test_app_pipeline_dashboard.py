"""Comprobaciones del botón de dashboard en la app pipeline."""

from __future__ import annotations

from pathlib import Path
import sys

RAIZ_PROYECTO = Path(__file__).resolve().parents[1]
if str(RAIZ_PROYECTO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROYECTO))

from app_pipeline import app


def test_abrir_dashboard_si_ya_responde(monkeypatch):
    """Si el dashboard responde, solo abre el navegador."""
    abiertos = []

    monkeypatch.setattr(app, "_dashboard_responde", lambda: True)
    monkeypatch.setattr(app, "_arrancar_dashboard", lambda: (_ for _ in ()).throw(AssertionError))
    monkeypatch.setattr(app.webbrowser, "open", abiertos.append)

    ok, mensaje = app.abrir_dashboard_desde_pipeline()

    assert ok is True
    assert mensaje == "Dashboard abierto."
    assert abiertos == [app.URL_DASHBOARD]


def test_abrir_dashboard_no_duplica_si_puerto_esta_ocupado(monkeypatch):
    """Si el puerto ya está ocupado, espera pero no lanza otro proceso."""
    abiertos = []

    monkeypatch.setattr(app, "_dashboard_responde", lambda: False)
    monkeypatch.setattr(app, "_puerto_dashboard_activo", lambda: True)
    monkeypatch.setattr(app, "_esperar_dashboard", lambda: True)
    monkeypatch.setattr(app, "_arrancar_dashboard", lambda: (_ for _ in ()).throw(AssertionError))
    monkeypatch.setattr(app.webbrowser, "open", abiertos.append)

    ok, mensaje = app.abrir_dashboard_desde_pipeline()

    assert ok is True
    assert mensaje == "Dashboard abierto."
    assert abiertos == [app.URL_DASHBOARD]


def test_abrir_dashboard_arranca_si_no_responde(monkeypatch):
    """Si no hay dashboard activo, lanza el script y abre al responder."""
    class Proceso:
        def poll(self):
            return None

    class Script:
        def exists(self):
            return True

    abiertos = []
    lanzados = []

    monkeypatch.setattr(app, "_dashboard_responde", lambda: False)
    monkeypatch.setattr(app, "_puerto_dashboard_activo", lambda: False)
    monkeypatch.setattr(app, "SCRIPT_DASHBOARD", Script())
    monkeypatch.setattr(app, "_arrancar_dashboard", lambda: lanzados.append(True) or Proceso())
    monkeypatch.setattr(app, "_esperar_dashboard", lambda: True)
    monkeypatch.setattr(app.webbrowser, "open", abiertos.append)

    ok, mensaje = app.abrir_dashboard_desde_pipeline()

    assert ok is True
    assert mensaje == "Dashboard abierto."
    assert lanzados == [True]
    assert abiertos == [app.URL_DASHBOARD]
