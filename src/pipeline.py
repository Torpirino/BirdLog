"""Orquesta el flujo completo Plaud → Supabase → backup."""

from pathlib import Path
from tempfile import TemporaryDirectory

from src.backup.exportar import hacer_backup
from src.config import cargar_config
from src.conexion import get_cliente
from src.drive.cliente import get_drive
from src.drive.operaciones import descargar_archivo, listar_txt, mover_archivo
from src.insercion.escritura import insertar_registro
from src.parser.normalizacion import normalizar_registro
from src.parser.plaud import parsear_txt_plaud
from src.parser.validacion import validar_registro


def procesar_drive() -> list[dict]:
    """Procesa todos los TXT de la carpeta de entrada."""
    config = cargar_config()
    cliente = get_cliente()
    drive = get_drive()
    resultados = []
    for archivo in listar_txt(config.DRIVE_ENTRADA_ID, drive):
        resultados.append(_procesar_archivo_drive(archivo, config, cliente, drive))
    return resultados


def _procesar_archivo_drive(archivo: dict, config, cliente, drive) -> dict:
    """Procesa un TXT concreto de Drive."""
    with TemporaryDirectory() as temporal:
        ruta = descargar_archivo(archivo["id"], Path(temporal) / archivo["name"], drive)
        try:
            resumen = procesar_txt_local(ruta, cliente, drive, config.DRIVE_BACKUPS_ID)
        except ValueError as exc:
            mover_archivo(archivo, config.DRIVE_ERRORES_ID, drive)
            return _resultado_error(archivo, str(exc))
        mover_archivo(archivo, config.DRIVE_PROCESADOS_ID, drive)
        return {"archivo": archivo["name"], "estado": "procesado", "resumen": resumen}


def procesar_txt_local(ruta: str | Path, cliente, drive=None, drive_backups_id: str | None = None) -> dict:
    """Parsea, valida, inserta y hace backup de un TXT local."""
    registro = normalizar_registro(parsear_txt_plaud(str(ruta)))
    errores = validar_registro(registro)
    if errores:
        raise ValueError(_mensaje_validacion(ruta, errores))
    resumen = insertar_registro(registro, cliente)
    carpeta_backup = hacer_backup(cliente)
    resumen["backup"] = str(carpeta_backup)
    return resumen


def _mensaje_validacion(ruta: str | Path, errores: list[str]) -> str:
    """Construye un mensaje claro de errores de validación."""
    detalle = "\n".join(f"- {error}" for error in errores)
    return f"El archivo {Path(ruta).name} no es válido:\n{detalle}"


def _resultado_error(archivo: dict, mensaje: str) -> dict:
    """Devuelve un resumen de error de procesamiento."""
    return {"archivo": archivo["name"], "estado": "error", "mensaje": mensaje}
