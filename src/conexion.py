"""Crea el cliente único de Supabase."""

from src.config import get_supabase_key, get_supabase_url

_CLIENTE = None
MENSAJE_PAUSA = "El proyecto Supabase está pausado.\nReactívalo en supabase.com y vuelve a intentarlo."


def get_cliente():
    """Devuelve una instancia compartida del cliente Supabase."""
    global _CLIENTE
    if _CLIENTE is None:
        _CLIENTE = _crear_cliente()
    return _CLIENTE


def _crear_cliente():
    """Construye el cliente y traduce errores de conexión."""
    try:
        from supabase import create_client

        return create_client(get_supabase_url(), get_supabase_key())
    except Exception as exc:
        if _parece_proyecto_pausado(exc):
            raise RuntimeError(MENSAJE_PAUSA) from exc
        raise


def _parece_proyecto_pausado(error: Exception) -> bool:
    """Detecta errores frecuentes cuando Supabase está pausado."""
    texto = str(error).lower()
    pistas = ["paused", "pause", "connection", "timeout", "resolve", "refused", "unreachable"]
    return any(pista in texto for pista in pistas)
