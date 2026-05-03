"""Tests de perfiles de configuración."""

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import cargar_config_dashboard, cargar_config_fotos, cargar_config_pipeline


VARIABLES_ENV = [
    "ENTORNO",
    "SUPABASE_DEV_URL",
    "SUPABASE_DEV_KEY",
    "SUPABASE_PROD_URL",
    "SUPABASE_PROD_KEY",
    "GOOGLE_CREDENTIALS_PATH",
    "DRIVE_ENTRADA_ID",
    "DRIVE_PROCESADOS_ID",
    "DRIVE_ERRORES_ID",
    "DRIVE_BACKUPS_ID",
    "DRIVE_FOTOS_ID",
]


def _limpiar_env(monkeypatch):
    for variable in VARIABLES_ENV:
        monkeypatch.setenv(variable, "")


def _env_pipeline(monkeypatch):
    monkeypatch.setenv("ENTORNO", "dev")
    monkeypatch.setenv("SUPABASE_DEV_URL", "https://dev.supabase.co")
    monkeypatch.setenv("SUPABASE_DEV_KEY", "dev-key")
    monkeypatch.setenv("GOOGLE_CREDENTIALS_PATH", "/tmp/credenciales.json")
    monkeypatch.setenv("DRIVE_ENTRADA_ID", "entrada")
    monkeypatch.setenv("DRIVE_PROCESADOS_ID", "procesados")
    monkeypatch.setenv("DRIVE_ERRORES_ID", "errores")


def test_config_pipeline_no_exige_drive_fotos_id(monkeypatch):
    """El pipeline Plaud no depende de la carpeta de fotos."""
    _limpiar_env(monkeypatch)
    _env_pipeline(monkeypatch)
    config = cargar_config_pipeline()
    assert config.DRIVE_ENTRADA_ID == "entrada"
    assert config.DRIVE_FOTOS_ID == ""


def test_config_fotos_exige_drive_fotos_id(monkeypatch):
    """El perfil de fotos sí valida su carpeta raíz de Drive."""
    _limpiar_env(monkeypatch)
    _env_pipeline(monkeypatch)
    with pytest.raises(RuntimeError, match="DRIVE_FOTOS_ID"):
        cargar_config_fotos()


def test_config_pipeline_exige_drive_entrada_id(monkeypatch):
    """Las carpetas necesarias para Plaud siguen siendo obligatorias."""
    _limpiar_env(monkeypatch)
    _env_pipeline(monkeypatch)
    monkeypatch.setenv("DRIVE_ENTRADA_ID", "")
    with pytest.raises(RuntimeError, match="DRIVE_ENTRADA_ID"):
        cargar_config_pipeline()


def test_config_dashboard_no_exige_drive(monkeypatch):
    """El dashboard solo necesita Supabase del entorno activo."""
    _limpiar_env(monkeypatch)
    monkeypatch.setenv("ENTORNO", "dev")
    monkeypatch.setenv("SUPABASE_DEV_URL", "https://dev.supabase.co")
    monkeypatch.setenv("SUPABASE_DEV_KEY", "dev-key")
    config = cargar_config_dashboard()
    assert config.ENTORNO == "dev"
