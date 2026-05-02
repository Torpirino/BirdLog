"""Conexión segura del dashboard con Supabase."""

from dataclasses import dataclass
from pathlib import Path
import os


MENSAJE_PAUSA = (
    "El proyecto Supabase está pausado. Reactívalo en supabase.com y vuelve a intentarlo."
)


@dataclass(frozen=True)
class EstadoConexion:
    """Resultado legible de una comprobación de conexión."""

    ok: bool
    mensaje: str
    entorno: str = "dev"


def get_cliente():
    """Crea un cliente Supabase usando las variables existentes del proyecto."""
    url, key, _ = _leer_credenciales_supabase()
    try:
        from supabase import create_client
    except ImportError as exc:
        raise RuntimeError("Falta instalar la dependencia supabase.") from exc

    try:
        return create_client(url, key)
    except Exception as exc:
        raise RuntimeError(_traducir_error(exc)) from exc


def probar_conexion() -> EstadoConexion:
    """Comprueba configuración básica sin exponer credenciales."""
    try:
        cliente = get_cliente()
        cliente.table("visitas").select("id_visita").limit(1).execute()
    except RuntimeError as exc:
        return EstadoConexion(False, str(exc), _leer_entorno())
    except Exception as exc:
        return EstadoConexion(False, _traducir_error(exc), _leer_entorno())
    return EstadoConexion(True, "Conectado a Supabase dev.", _leer_entorno())


def _leer_credenciales_supabase() -> tuple[str, str, str]:
    """Lee solo las credenciales Supabase necesarias para el dashboard."""
    _cargar_dotenv()
    entorno = _leer_entorno()
    if entorno == "prod":
        raise RuntimeError("Prod está bloqueado en esta fase. Usa ENTORNO=dev.")

    url = os.getenv("SUPABASE_DEV_URL", "").strip()
    key = os.getenv("SUPABASE_DEV_KEY", "").strip()
    faltan = [
        nombre
        for nombre, valor in (("SUPABASE_DEV_URL", url), ("SUPABASE_DEV_KEY", key))
        if not valor
    ]
    if faltan:
        raise RuntimeError(f"Faltan credenciales Supabase en .env: {', '.join(faltan)}")
    if not url.startswith("https://"):
        raise RuntimeError("La URL de Supabase no parece válida.")
    return url, key, entorno


def _leer_entorno() -> str:
    """Devuelve el entorno activo, por defecto dev."""
    return os.getenv("ENTORNO", "dev").strip() or "dev"


def _cargar_dotenv() -> None:
    """Carga .env si python-dotenv está disponible."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(Path(".env"))


def _traducir_error(error: Exception) -> str:
    """Convierte errores técnicos en mensajes útiles para el observador."""
    texto = str(error).lower()
    if any(pista in texto for pista in ("paused", "pause", "timeout", "unreachable")):
        return MENSAJE_PAUSA
    if any(pista in texto for pista in ("resolve", "connection", "refused")):
        return "Supabase no responde. Revisa conexión a internet o si el proyecto está activo."
    if any(pista in texto for pista in ("jwt", "invalid api key", "unauthorized")):
        return "La URL o la clave de Supabase no son válidas."
    if any(pista in texto for pista in ("permission", "forbidden", "rls")):
        return "Supabase ha rechazado la consulta por permisos."
    return "No se pudo conectar con Supabase. Revisa la configuración local."
