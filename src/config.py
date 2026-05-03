"""Carga y valida la configuración local del sistema."""

from dataclasses import dataclass
from pathlib import Path
import os


VARIABLES_ENTORNO = ["ENTORNO"]
VARIABLES_SUPABASE = ["SUPABASE_DEV_URL", "SUPABASE_DEV_KEY", "SUPABASE_PROD_URL", "SUPABASE_PROD_KEY"]

VARIABLES_DRIVE = [
    "GOOGLE_CREDENTIALS_PATH",
]

VARIABLES_PIPELINE = [
    *VARIABLES_DRIVE,
    "DRIVE_ENTRADA_ID",
    "DRIVE_PROCESADOS_ID",
    "DRIVE_ERRORES_ID",
]

VARIABLES_FOTOS = [
    *VARIABLES_DRIVE,
    "DRIVE_FOTOS_ID",
]

VARIABLES_OBLIGATORIAS = [
    *VARIABLES_ENTORNO,
    *VARIABLES_SUPABASE,
    *VARIABLES_PIPELINE,
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


@dataclass(frozen=True)
class ConfigDashboard:
    """Configuración mínima para consultar Supabase."""

    ENTORNO: str = ""
    SUPABASE_DEV_URL: str = ""
    SUPABASE_DEV_KEY: str = ""
    SUPABASE_PROD_URL: str = ""
    SUPABASE_PROD_KEY: str = ""


@dataclass(frozen=True)
class ConfigDrive:
    """Configuración mínima para autenticar Google Drive."""

    ENTORNO: str = ""
    SUPABASE_DEV_URL: str = ""
    SUPABASE_DEV_KEY: str = ""
    SUPABASE_PROD_URL: str = ""
    SUPABASE_PROD_KEY: str = ""
    GOOGLE_CREDENTIALS_PATH: str = ""


@dataclass(frozen=True)
class ConfigPipeline:
    """Configuración necesaria para procesar archivos Plaud."""

    ENTORNO: str = ""
    SUPABASE_DEV_URL: str = ""
    SUPABASE_DEV_KEY: str = ""
    SUPABASE_PROD_URL: str = ""
    SUPABASE_PROD_KEY: str = ""
    GOOGLE_CREDENTIALS_PATH: str = ""
    DRIVE_ENTRADA_ID: str = ""
    DRIVE_PROCESADOS_ID: str = ""
    DRIVE_ERRORES_ID: str = ""
    DRIVE_BACKUPS_ID: str = ""
    DRIVE_FOTOS_ID: str = ""


@dataclass(frozen=True)
class ConfigFotos:
    """Configuración necesaria para sincronizar fotos."""

    ENTORNO: str = ""
    SUPABASE_DEV_URL: str = ""
    SUPABASE_DEV_KEY: str = ""
    SUPABASE_PROD_URL: str = ""
    SUPABASE_PROD_KEY: str = ""
    GOOGLE_CREDENTIALS_PATH: str = ""
    DRIVE_FOTOS_ID: str = ""


def cargar_config() -> Config:
    """Carga .env y devuelve la configuración completa histórica."""
    valores = _cargar_y_validar(VARIABLES_OBLIGATORIAS)
    return Config(**valores)


def cargar_config_dashboard() -> ConfigDashboard:
    """Carga configuración mínima para el dashboard."""
    valores = _cargar_y_validar_perfil([])
    return ConfigDashboard(**valores)


def cargar_config_drive() -> ConfigDrive:
    """Carga configuración mínima para autenticar Google Drive."""
    valores = _cargar_y_validar_perfil(VARIABLES_DRIVE)
    return ConfigDrive(**valores)


def cargar_config_pipeline() -> ConfigPipeline:
    """Carga configuración necesaria para el pipeline Plaud."""
    valores = _cargar_y_validar_perfil(VARIABLES_PIPELINE)
    valores["DRIVE_BACKUPS_ID"] = os.getenv("DRIVE_BACKUPS_ID", "").strip()
    valores["DRIVE_FOTOS_ID"] = os.getenv("DRIVE_FOTOS_ID", "").strip()
    return ConfigPipeline(**valores)


def cargar_config_fotos() -> ConfigFotos:
    """Carga configuración necesaria para sincronizar fotos."""
    valores = _cargar_y_validar_perfil(VARIABLES_FOTOS)
    return ConfigFotos(**valores)


def get_supabase_url() -> str:
    """Devuelve la URL Supabase del entorno activo."""
    config = cargar_config_dashboard()
    return config.SUPABASE_DEV_URL if config.ENTORNO == "dev" else config.SUPABASE_PROD_URL


def get_supabase_key() -> str:
    """Devuelve la clave Supabase del entorno activo."""
    config = cargar_config_dashboard()
    return config.SUPABASE_DEV_KEY if config.ENTORNO == "dev" else config.SUPABASE_PROD_KEY


def _cargar_dotenv() -> None:
    """Carga variables desde .env usando python-dotenv."""
    try:
        from dotenv import load_dotenv
    except ImportError as exc:
        raise RuntimeError("Falta instalar python-dotenv para cargar el archivo .env.") from exc
    load_dotenv(Path(".env"))


def _cargar_y_validar(variables: list[str]) -> dict[str, str]:
    """Carga .env y valida solo las variables del perfil solicitado."""
    _cargar_dotenv()
    valores = {nombre: os.getenv(nombre, "").strip() for nombre in variables}
    _validar_valores(valores)
    return valores


def _cargar_y_validar_perfil(variables_extra: list[str]) -> dict[str, str]:
    """Carga .env y valida Supabase activo más variables del perfil."""
    _cargar_dotenv()
    entorno = os.getenv("ENTORNO", "").strip()
    _validar_valores({"ENTORNO": entorno})
    variables = _variables_supabase_activas(entorno) + variables_extra
    valores = {"ENTORNO": entorno}
    valores.update({nombre: os.getenv(nombre, "").strip() for nombre in variables})
    _validar_valores(valores)
    return valores


def _variables_supabase_activas(entorno: str) -> list[str]:
    """Devuelve las variables Supabase que requiere el entorno activo."""
    if entorno == "dev":
        return ["SUPABASE_DEV_URL", "SUPABASE_DEV_KEY"]
    return ["SUPABASE_PROD_URL", "SUPABASE_PROD_KEY"]


def _validar_valores(valores: dict[str, str]) -> None:
    """Lanza errores claros si falta configuración."""
    faltan = [nombre for nombre, valor in valores.items() if not valor]
    if faltan:
        raise RuntimeError(f"Faltan variables obligatorias en .env: {', '.join(faltan)}")
    if valores["ENTORNO"] not in {"dev", "prod"}:
        raise RuntimeError("ENTORNO debe ser 'dev' o 'prod'.")
    if valores["ENTORNO"] == "prod":
        raise RuntimeError("Prod está bloqueado en esta fase. Usa ENTORNO=dev.")
