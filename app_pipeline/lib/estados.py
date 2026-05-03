"""Constantes y modelo de datos de resultado para la app pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


ESTADO_OK = "OK"
ESTADO_ERROR = "ERROR"
ESTADO_INCOMPLETO = "INCOMPLETO"
ESTADO_PENDIENTE = "PENDIENTE"

ICONO: dict[str, str] = {
    ESTADO_OK: "🟢",
    ESTADO_ERROR: "🔴",
    ESTADO_INCOMPLETO: "🟡",
    ESTADO_PENDIENTE: "⚪",
}

ETIQUETA: dict[str, str] = {
    ESTADO_OK: "Procesado correctamente",
    ESTADO_ERROR: "Error",
    ESTADO_INCOMPLETO: "Catálogo no encontrado",
    ESTADO_PENDIENTE: "Pendiente",
}


@dataclass(frozen=True)
class ResultadoArchivo:
    """Resultado de procesar un archivo Plaud."""

    nombre: str
    estado: Literal["OK", "ERROR", "INCOMPLETO", "PENDIENTE"]
    etapa: str
    mensaje: str
    txt_movido_a: Literal["procesados", "errores", "-"]
    insertado_supabase: bool
    backup_creado: bool


@dataclass(frozen=True)
class EstadoEntorno:
    """Estado del entorno: configuración, Drive y Supabase."""

    ok: bool
    entorno: str
    drive_ok: bool
    supabase_ok: bool
    mensaje: str
