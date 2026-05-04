"""Wrapper sobre src.pipeline con traducción a estados visuales."""

from __future__ import annotations

from app_pipeline.lib.estados import (
    ESTADO_ERROR,
    ESTADO_INCOMPLETO,
    ESTADO_OK,
    EstadoEntorno,
    ResultadoArchivo,
)


def comprobar_entorno() -> EstadoEntorno:
    """Valida configuración, Drive y Supabase antes de procesar."""
    try:
        from src.config import cargar_config_pipeline
        config = cargar_config_pipeline()
    except RuntimeError as exc:
        return EstadoEntorno(
            ok=False,
            entorno="?",
            drive_ok=False,
            supabase_ok=False,
            mensaje=str(exc),
        )

    entorno = config.ENTORNO

    try:
        from src.drive.cliente import get_drive
        get_drive()
    except Exception:
        return EstadoEntorno(
            ok=False,
            entorno=entorno,
            drive_ok=False,
            supabase_ok=False,
            mensaje=(
                "No se pudo acceder a Google Drive. "
                "Revisa el archivo de credenciales y los IDs de carpeta en `.env`."
            ),
        )

    try:
        from src.conexion import get_cliente
        cliente = get_cliente()
        cliente.table("visitas").select("id_visita").limit(1).execute()
    except RuntimeError as exc:
        return EstadoEntorno(
            ok=False,
            entorno=entorno,
            drive_ok=True,
            supabase_ok=False,
            mensaje=str(exc),
        )
    except Exception:
        return EstadoEntorno(
            ok=False,
            entorno=entorno,
            drive_ok=True,
            supabase_ok=False,
            mensaje="No se pudo conectar con Supabase. Revisa la configuración local.",
        )

    return EstadoEntorno(
        ok=True,
        entorno=entorno,
        drive_ok=True,
        supabase_ok=True,
        mensaje="",
    )


def procesar_lote() -> list[ResultadoArchivo]:
    """Lanza el pipeline completo y traduce resultados a objetos con estado de color."""
    from src.pipeline import procesar_drive

    try:
        resultados_raw = procesar_drive()
    except RuntimeError as exc:
        return [
            ResultadoArchivo(
                nombre="— lote completo —",
                estado=ESTADO_ERROR,
                etapa="Conexión",
                mensaje=str(exc),
                txt_movido_a="-",
                insertado_supabase=False,
                backup_creado=False,
            )
        ]

    return [_traducir_resultado(r) for r in resultados_raw]


def _traducir_resultado(raw: dict) -> ResultadoArchivo:
    """Convierte el dict del pipeline a un ResultadoArchivo con estado de color."""
    nombre = raw.get("archivo", "desconocido")

    if raw.get("estado") == "procesado":
        resumen = raw.get("resumen", {})
        return ResultadoArchivo(
            nombre=nombre,
            estado=ESTADO_OK,
            etapa="Backup",
            mensaje=_resumen_legible(resumen),
            txt_movido_a="procesados",
            insertado_supabase=True,
            backup_creado=bool(resumen.get("backup")),
        )

    mensaje = raw.get("mensaje", "Error desconocido.")
    estado, etapa = _clasificar_error(mensaje)
    if raw.get("fase") == "catálogo/FK":
        estado, etapa = ESTADO_INCOMPLETO, "Resolución de catálogos/FK"
    elif raw.get("fase"):
        etapa = str(raw["fase"]).capitalize()
    return ResultadoArchivo(
        nombre=nombre,
        estado=estado,
        etapa=etapa,
        mensaje=mensaje,
        txt_movido_a="errores",
        insertado_supabase=False,
        backup_creado=False,
        diagnosticos=tuple(raw.get("errores", ())),
    )


def _clasificar_error(mensaje: str) -> tuple[str, str]:
    """Clasifica el error por subcadena del mensaje del pipeline."""
    m = mensaje.lower()
    if "catálogo/fk" in m or any(p in m for p in ("lugar no encontrado", "observador no encontrado", "especie no encontrada")):
        return ESTADO_INCOMPLETO, "Resolución de catálogos/FK"
    if "fase': 'catálogo/fk" in m:
        return ESTADO_INCOMPLETO, "Resolución de catálogos/FK"
    if any(p in m for p in ("lugar no encontrado", "observador no encontrado", "especie no encontrada")):
        return ESTADO_INCOMPLETO, "Resolución de catálogos/FK"
    if "no es válido" in m:
        return ESTADO_ERROR, "Validación"
    if "pausado" in m:
        return ESTADO_ERROR, "Conexión"
    return ESTADO_ERROR, "Procesamiento"


def _resumen_legible(resumen: dict) -> str:
    """Convierte el dict resumen de pipeline a texto legible para el observador."""
    if resumen.get("mensaje"):
        return resumen["mensaje"]
    tipo = resumen.get("tipo_visita", resumen.get("tipo", ""))
    id_visita = resumen.get("id_visita", "")
    partes = []
    if tipo:
        partes.append(f"Tipo: {tipo}")
    if id_visita:
        partes.append(f"visita id={id_visita}")
    return ", ".join(partes) if partes else "Insertado en Supabase correctamente."
