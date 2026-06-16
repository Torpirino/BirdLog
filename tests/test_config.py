"""Tests de perfiles de configuración."""

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import cargar_config_fotos, cargar_config_supabase


VARIABLES_ENV = [
    "ENTORNO",
    "SUPABASE_DEV_URL",
    "SUPABASE_DEV_KEY",
    "SUPABASE_PROD_URL",
    "SUPABASE_PROD_KEY",
    "GOOGLE_CREDENTIALS_PATH",
    "DRIVE_BACKUPS_ID",
    "DRIVE_FOTOS_ID",
]


def _limpiar_env(monkeypatch):
    for variable in VARIABLES_ENV:
        monkeypatch.setenv(variable, "")


def test_config_supabase_solo_necesita_supabase(monkeypatch):
    """El perfil Supabase no exige variables de Drive."""
    _limpiar_env(monkeypatch)
    monkeypatch.setenv("ENTORNO", "dev")
    monkeypatch.setenv("SUPABASE_DEV_URL", "https://dev.supabase.co")
    monkeypatch.setenv("SUPABASE_DEV_KEY", "dev-key")
    config = cargar_config_supabase()
    assert config.ENTORNO == "dev"
    assert config.SUPABASE_DEV_URL == "https://dev.supabase.co"


def test_config_supabase_falla_sin_entorno(monkeypatch):
    """Falla si ENTORNO no está definido."""
    _limpiar_env(monkeypatch)
    with pytest.raises(RuntimeError, match="ENTORNO"):
        cargar_config_supabase()


def test_config_fotos_exige_drive_fotos_id(monkeypatch):
    """El perfil de fotos valida su carpeta raíz de Drive."""
    _limpiar_env(monkeypatch)
    monkeypatch.setenv("ENTORNO", "dev")
    monkeypatch.setenv("SUPABASE_DEV_URL", "https://dev.supabase.co")
    monkeypatch.setenv("SUPABASE_DEV_KEY", "dev-key")
    monkeypatch.setenv("GOOGLE_CREDENTIALS_PATH", "/tmp/credenciales.json")
    with pytest.raises(RuntimeError, match="DRIVE_FOTOS_ID"):
        cargar_config_fotos()


def test_config_fotos_ok_con_todas_las_variables(monkeypatch):
    """El perfil de fotos arranca cuando todas las variables están presentes."""
    _limpiar_env(monkeypatch)
    monkeypatch.setenv("ENTORNO", "dev")
    monkeypatch.setenv("SUPABASE_DEV_URL", "https://dev.supabase.co")
    monkeypatch.setenv("SUPABASE_DEV_KEY", "dev-key")
    monkeypatch.setenv("GOOGLE_CREDENTIALS_PATH", "/tmp/credenciales.json")
    monkeypatch.setenv("DRIVE_FOTOS_ID", "fotos-id")
    config = cargar_config_fotos()
    assert config.DRIVE_FOTOS_ID == "fotos-id"
