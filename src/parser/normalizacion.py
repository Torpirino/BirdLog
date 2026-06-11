"""Normaliza variantes frecuentes de registros Plaud."""

from copy import deepcopy
from datetime import datetime
import re

NUMEROS = {
    "cero": 0,
    "uno": 1,
    "dos": 2,
    "tres": 3,
    "cuatro": 4,
    "cinco": 5,
    "seis": 6,
    "siete": 7,
    "ocho": 8,
    "nueve": 9,
    "diez": 10,
    "once": 11,
    "doce": 12,
    "trece": 13,
    "catorce": 14,
    "quince": 15,
    "dieciseis": 16,
    "dieciséis": 16,
    "diecisiete": 17,
    "dieciocho": 18,
    "diecinueve": 19,
    "veinte": 20,
}
TEXTOS_LIBRES = {"texto_revision"} | {f"observaciones_{sufijo}" for sufijo in ("visita", "meteo", "caja", "cebo", "nido", "puente", "mamifero")}


def normalizar_registro(registro: dict) -> dict:
    """Devuelve una copia normalizada de un registro parseado."""
    normalizado = deepcopy(registro)
    for bloque in _iter_bloques(normalizado):
        _normalizar_bloque(bloque)
    return normalizado


def _normalizar_bloque(bloque: dict) -> None:
    """Aplica normalizaciones campo a campo."""
    for campo, valor in list(bloque.items()):
        if campo in TEXTOS_LIBRES or not isinstance(valor, str):
            continue
        if campo == "lugar_caja":
            bloque[campo] = _normalizar_caja(valor)
        elif campo == "lugar_cebo":
            bloque[campo] = _normalizar_cebo(valor)
        elif campo in {"ocupada", "incuba"}:
            bloque[campo] = _normalizar_booleano(valor)
        elif campo == "comportamiento":
            bloque[campo] = _normalizar_comportamiento(valor)
        elif campo in {"fecha", "fecha_colocacion"}:
            bloque[campo] = normalizar_fecha(valor)


def normalizar_fecha(valor: str) -> str:
    """Convierte fechas aceptadas al formato interno YYYY-MM-DD."""
    limpio = valor.strip()
    formatos = (
        (r"\d{4}-\d{2}-\d{2}", "%Y-%m-%d"),
        (r"\d{2}/\d{2}/\d{4}", "%d/%m/%Y"),
    )
    for patron, formato in formatos:
        if not re.fullmatch(patron, limpio):
            continue
        try:
            return datetime.strptime(limpio, formato).date().isoformat()
        except ValueError:
            continue
    return valor


def _iter_bloques(registro: dict):
    """Itera todos los bloques mutables de un registro."""
    yield registro.get("visita", {})
    yield from registro.get("meteorologia", [])
    yield from registro.get("datos", [])


def _normalizar_caja(valor: str) -> str:
    """Convierte códigos hablados de caja al formato BAR01."""
    partes = _partes_limpias(valor)
    letras = "".join(parte.upper() for parte in partes if parte.isalpha() and parte not in NUMEROS and parte != "caja")
    numero = _extraer_numero(partes)
    if letras and numero is not None:
        return f"{letras}{numero:02d}"
    return valor


def _normalizar_cebo(valor: str) -> str:
    """Convierte nombres hablados de cebo al formato de catálogo."""
    numero = _extraer_numero(_partes_limpias(valor))
    if numero is None:
        return valor
    return f"Cebo avispón {numero}"


def _normalizar_booleano(valor: str):
    """Convierte variantes textuales de booleano."""
    limpio = valor.strip().lower()
    if limpio in {"sí", "si", "yes", "1", "true"}:
        return True
    if limpio in {"no", "0", "false"}:
        return False
    return valor


def _normalizar_comportamiento(valor: str) -> str:
    """Normaliza variantes menores de comportamiento Lindus."""
    limpio = valor.strip().lower()
    variantes = {"migrador": "MIGRADOR", "migradores": "MIGRADOR", "norte": "NORTE", "local": "LOCAL", "locales": "LOCAL"}
    if valor in {"MIGRADOR", "NORTE", "LOCAL"}:
        return valor
    return variantes.get(limpio, valor)


def _partes_limpias(valor: str) -> list[str]:
    """Divide texto sencillo en partes normalizadas."""
    limpio = valor.lower().replace(",", " ").replace("-", " ")
    return [parte for parte in limpio.split() if parte not in {"avispón", "avispon", "asiático", "asiatico", "número", "numero"}]


def _extraer_numero(partes: list[str]) -> int | None:
    """Obtiene un número a partir de dígitos o palabras."""
    digitos = "".join(parte for parte in partes if parte.isdigit())
    if digitos:
        return int(digitos)
    encontrados = [NUMEROS[parte] for parte in partes if parte in NUMEROS]
    if not encontrados:
        return None
    if encontrados[:2] == [0, 1]:
        return 1
    return encontrados[-1]
