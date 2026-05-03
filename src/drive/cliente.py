"""Crea el cliente de Google Drive."""

from src.config import cargar_config_drive


def get_drive():
    """Devuelve un cliente autenticado de Google Drive."""
    config = cargar_config_drive()
    try:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
    except ImportError as exc:
        raise RuntimeError("Falta instalar google-api-python-client y google-auth.") from exc
    scopes = ["https://www.googleapis.com/auth/drive"]
    credenciales = Credentials.from_service_account_file(config.GOOGLE_CREDENTIALS_PATH, scopes=scopes)
    return build("drive", "v3", credentials=credenciales)
