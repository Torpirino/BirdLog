"""Tests del orquestador de la app pipeline (sin dependencias externas)."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app_pipeline.lib.orquestador import (
    _clasificar_error,
    _resumen_legible,
    _traducir_resultado,
    procesar_lote,
)
from app_pipeline.lib.estados import ESTADO_ERROR, ESTADO_INCOMPLETO, ESTADO_OK


# ---------------------------------------------------------------------------
# Clasificación de errores
# ---------------------------------------------------------------------------

def test_clasificar_error_lugar_no_encontrado():
    estado, etapa = _clasificar_error("Lugar no encontrado: 'Altzania'")
    assert estado == ESTADO_INCOMPLETO
    assert "catálogos" in etapa.lower()


def test_clasificar_error_observador_no_encontrado():
    estado, _ = _clasificar_error("Observador no encontrado: 'Mikel'")
    assert estado == ESTADO_INCOMPLETO


def test_clasificar_error_especie_no_encontrada():
    estado, _ = _clasificar_error("Especie no encontrada: 'milano negro'")
    assert estado == ESTADO_INCOMPLETO


def test_clasificar_error_validacion():
    estado, etapa = _clasificar_error(
        "El archivo visita.txt no es válido:\n- Falta campo obligatorio 'fecha'"
    )
    assert estado == ESTADO_ERROR
    assert "validación" in etapa.lower()


def test_clasificar_error_supabase_pausado():
    estado, etapa = _clasificar_error(
        "El proyecto Supabase está pausado. Reactívalo en supabase.com."
    )
    assert estado == ESTADO_ERROR
    assert "conexión" in etapa.lower()


def test_clasificar_error_generico_devuelve_error():
    estado, etapa = _clasificar_error("Error inesperado de red al conectar")
    assert estado == ESTADO_ERROR
    assert etapa == "Procesamiento"


# ---------------------------------------------------------------------------
# Resumen legible
# ---------------------------------------------------------------------------

def test_resumen_legible_con_tipo_e_id():
    resumen = {"tipo_visita": "LINDUS", "id_visita": 42}
    texto = _resumen_legible(resumen)
    assert "LINDUS" in texto
    assert "42" in texto


def test_resumen_legible_sin_datos_devuelve_texto_generico():
    texto = _resumen_legible({})
    assert len(texto) > 0


# ---------------------------------------------------------------------------
# Traducción de resultado procesado
# ---------------------------------------------------------------------------

def test_traducir_resultado_procesado_es_ok():
    raw = {
        "archivo": "visita_lindus.txt",
        "estado": "procesado",
        "resumen": {"backup": "/backups/2026-05-03", "id_visita": 7},
    }
    resultado = _traducir_resultado(raw)
    assert resultado.estado == ESTADO_OK
    assert resultado.insertado_supabase is True
    assert resultado.backup_creado is True
    assert resultado.txt_movido_a == "procesados"
    assert resultado.nombre == "visita_lindus.txt"


def test_traducir_resultado_procesado_sin_backup():
    raw = {
        "archivo": "visita.txt",
        "estado": "procesado",
        "resumen": {"id_visita": 3},
    }
    resultado = _traducir_resultado(raw)
    assert resultado.estado == ESTADO_OK
    assert resultado.backup_creado is False


def test_traducir_resultado_error_mueve_a_errores():
    raw = {
        "archivo": "visita.txt",
        "estado": "error",
        "mensaje": "El archivo visita.txt no es válido:\n- Falta 'fecha'",
    }
    resultado = _traducir_resultado(raw)
    assert resultado.estado == ESTADO_ERROR
    assert resultado.txt_movido_a == "errores"
    assert resultado.insertado_supabase is False


def test_traducir_resultado_catalogo_es_incompleto():
    raw = {
        "archivo": "caja.txt",
        "estado": "error",
        "mensaje": "Especie no encontrada: 'Nyctalus noctula'",
    }
    resultado = _traducir_resultado(raw)
    assert resultado.estado == ESTADO_INCOMPLETO


# ---------------------------------------------------------------------------
# procesar_lote con monkeypatch
# ---------------------------------------------------------------------------

def test_procesar_lote_traduce_resultado_ok(monkeypatch):
    import src.pipeline as _pipeline

    monkeypatch.setattr(
        _pipeline,
        "procesar_drive",
        lambda: [
            {
                "archivo": "visita_lindus.txt",
                "estado": "procesado",
                "resumen": {"backup": "/backups/2026-05-03", "id_visita": 1},
            }
        ],
    )
    resultados = procesar_lote()
    assert len(resultados) == 1
    assert resultados[0].estado == ESTADO_OK


def test_procesar_lote_clasifica_especie_no_encontrada_como_incompleto(monkeypatch):
    import src.pipeline as _pipeline

    monkeypatch.setattr(
        _pipeline,
        "procesar_drive",
        lambda: [
            {
                "archivo": "caja.txt",
                "estado": "error",
                "mensaje": "Especie no encontrada: 'milano negro'",
            }
        ],
    )
    resultados = procesar_lote()
    assert resultados[0].estado == ESTADO_INCOMPLETO


def test_procesar_lote_clasifica_validacion_como_error(monkeypatch):
    import src.pipeline as _pipeline

    monkeypatch.setattr(
        _pipeline,
        "procesar_drive",
        lambda: [
            {
                "archivo": "visita.txt",
                "estado": "error",
                "mensaje": "El archivo visita.txt no es válido:\n- Falta campo 'fecha'",
            }
        ],
    )
    resultados = procesar_lote()
    assert resultados[0].estado == ESTADO_ERROR


def test_procesar_lote_supabase_pausado_devuelve_error_global(monkeypatch):
    import src.pipeline as _pipeline

    def procesar_drive_pausado():
        raise RuntimeError(
            "El proyecto Supabase está pausado. Reactívalo en supabase.com y vuelve a intentarlo."
        )

    monkeypatch.setattr(_pipeline, "procesar_drive", procesar_drive_pausado)
    resultados = procesar_lote()
    assert len(resultados) == 1
    assert resultados[0].estado == ESTADO_ERROR
    assert "pausado" in resultados[0].mensaje.lower()


def test_procesar_lote_lote_vacio(monkeypatch):
    import src.pipeline as _pipeline

    monkeypatch.setattr(_pipeline, "procesar_drive", lambda: [])
    resultados = procesar_lote()
    assert resultados == []


# ---------------------------------------------------------------------------
# comprobar_entorno con monkeypatch
# ---------------------------------------------------------------------------

def test_comprobar_entorno_falta_env_devuelve_rojo(monkeypatch):
    import src.config as _config

    def cargar_config_falla():
        raise RuntimeError("Faltan variables obligatorias en .env: ENTORNO")

    monkeypatch.setattr(_config, "cargar_config", cargar_config_falla)

    from app_pipeline.lib.orquestador import comprobar_entorno
    estado = comprobar_entorno()
    assert estado.ok is False
    assert "Faltan" in estado.mensaje


def test_comprobar_entorno_drive_inaccesible_devuelve_no_ok(monkeypatch):
    import src.config as _config
    import src.drive.cliente as _drive_cliente

    from dataclasses import make_dataclass

    ConfigFalso = make_dataclass("Config", [("ENTORNO", str)] + [
        (v, str) for v in [
            "SUPABASE_DEV_URL", "SUPABASE_DEV_KEY", "SUPABASE_PROD_URL", "SUPABASE_PROD_KEY",
            "GOOGLE_CREDENTIALS_PATH", "DRIVE_ENTRADA_ID", "DRIVE_PROCESADOS_ID",
            "DRIVE_ERRORES_ID", "DRIVE_BACKUPS_ID", "DRIVE_FOTOS_ID",
        ]
    ])
    config_ok = ConfigFalso(
        ENTORNO="dev",
        SUPABASE_DEV_URL="https://x.supabase.co",
        SUPABASE_DEV_KEY="key",
        SUPABASE_PROD_URL="https://y.supabase.co",
        SUPABASE_PROD_KEY="key",
        GOOGLE_CREDENTIALS_PATH="/ruta/creds.json",
        DRIVE_ENTRADA_ID="id1",
        DRIVE_PROCESADOS_ID="id2",
        DRIVE_ERRORES_ID="id3",
        DRIVE_BACKUPS_ID="id4",
        DRIVE_FOTOS_ID="id5",
    )
    monkeypatch.setattr(_config, "cargar_config", lambda: config_ok)

    def get_drive_falla():
        raise Exception("Credenciales inválidas")

    monkeypatch.setattr(_drive_cliente, "get_drive", get_drive_falla)

    from app_pipeline.lib.orquestador import comprobar_entorno
    estado = comprobar_entorno()
    assert estado.ok is False
    assert estado.drive_ok is False
    assert "Drive" in estado.mensaje
