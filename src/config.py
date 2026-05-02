"""Carga y valida la configuración local del sistema."""

from dataclasses import dataclass
from pathlib import Path
import os


VARIABLES_OBLIGATORIAS = [
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


@dataclass(frozen=True)
class Config:
    """Agrupa las variables necesarias del entorno."""

    ENTORNO: str
    SUPABASE_DEV_URL: str
    SUPABASE_DEV_KEY: str
    SUPABASE_PROD_URL: str
    SUPABASE_PROD_KEY: str
    GOOGLE_CREDENTIALS_PATH: str
    DRIVE_ENTRADA_ID: str
    DRIVE_PROCESADOS_ID: str
    DRIVE_ERRORES_ID: str
    DRIVE_BACKUPS_ID: str
    DRIVE_FOTOS_ID: str


def cargar_config() -> Config:
    """Carga .env y devuelve configuración validada."""
    _cargar_dotenv()
    valores = {nombre: os.getenv(nombre, "").strip() for nombre in VARIABLES_OBLIGATORIAS}
    _validar_valores(valores)
    return Config(**valores)


def get_supabase_url() -> str:
    """Devuelve la URL Supabase del entorno activo."""
    config = cargar_config()
    return config.SUPABASE_DEV_URL if config.ENTORNO == "dev" else config.SUPABASE_PROD_URL


def get_supabase_key() -> str:
    """Devuelve la clave Supabase del entorno activo."""
    config = cargar_config()
    return config.SUPABASE_DEV_KEY if config.ENTORNO == "dev" else config.SUPABASE_PROD_KEY


def _cargar_dotenv() -> None:
    """Carga variables desde .env usando python-dotenv."""
    try:
        from dotenv import load_dotenv
    except ImportError as exc:
        raise RuntimeError("Falta instalar python-dotenv para cargar el archivo .env.") from exc
    load_dotenv(Path(".env"))


def _validar_valores(valores: dict[str, str]) -> None:
    """Lanza errores claros si falta configuración."""
    faltan = [nombre for nombre, valor in valores.items() if not valor]
    if faltan:
        raise RuntimeError(f"Faltan variables obligatorias en .env: {', '.join(faltan)}")
    if valores["ENTORNO"] not in {"dev", "prod"}:
        raise RuntimeError("ENTORNO debe ser 'dev' o 'prod'.")
    if valores["ENTORNO"] == "prod":
        raise RuntimeError("Prod está bloqueado en esta fase. Usa ENTORNO=dev.")
