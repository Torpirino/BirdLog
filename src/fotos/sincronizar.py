"""Sincroniza fotos de Drive con la tabla fotos."""

from datetime import date, datetime

from src.config import cargar_config
from src.conexion import get_cliente
from src.drive.cliente import get_drive

EXTENSIONES_IMAGEN = {".jpg", ".jpeg", ".png", ".heic"}


def sincronizar_fotos() -> list[dict]:
    """Escanea carpetas de fotos en Drive y registra URLs nuevas."""
    config = cargar_config()
    cliente = get_cliente()
    drive = get_drive()
    resultados = []
    for carpeta in _listar_subcarpetas(config.DRIVE_FOTOS_ID, drive):
        resultados.append(_procesar_carpeta(carpeta, cliente, drive))
    return resultados


def _parsear_nombre_carpeta(nombre: str) -> tuple[str, str] | None:
    """Extrae fecha y lugar de una carpeta YYYY-MM-DD_Lugar."""
    if "_" not in nombre:
        return None
    fecha, lugar = nombre.split("_", 1)
    if not lugar:
        return None
    try:
        datetime.strptime(fecha, "%Y-%m-%d")
    except ValueError:
        return None
    return fecha, lugar


def _procesar_carpeta(carpeta: dict, cliente, drive) -> dict:
    """Procesa una carpeta de fotos concreta."""
    parsed = _parsear_nombre_carpeta(carpeta["name"])
    if not parsed:
        return _aviso(carpeta, "Nombre de carpeta inválido")
    fecha, lugar = parsed
    id_visita = _buscar_visita(fecha, lugar, cliente)
    if id_visita is None:
        return _aviso(carpeta, f"Visita no encontrada para {fecha} {lugar}")
    return _insertar_fotos_carpeta(carpeta, id_visita, cliente, drive)


def _insertar_fotos_carpeta(carpeta: dict, id_visita: int, cliente, drive) -> dict:
    """Inserta las fotos nuevas de una carpeta válida."""
    nuevas = 0
    omitidas = 0
    for imagen in _listar_imagenes(carpeta["id"], drive):
        url = _url_drive(imagen["id"])
        if _foto_existe(url, cliente):
            omitidas += 1
            continue
        _insertar_foto(id_visita, url, cliente)
        nuevas += 1
    return {"carpeta": carpeta["name"], "estado": "procesada", "insertadas": nuevas, "omitidas": omitidas}


def _listar_subcarpetas(carpeta_id: str, drive) -> list[dict]:
    """Lista subcarpetas directas dentro de Fotos."""
    query = f"'{carpeta_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    respuesta = drive.files().list(q=query, fields="files(id,name)").execute()
    return respuesta.get("files", [])


def _listar_imagenes(carpeta_id: str, drive) -> list[dict]:
    """Lista archivos de imagen soportados dentro de una carpeta."""
    query = f"'{carpeta_id}' in parents and trashed=false"
    respuesta = drive.files().list(q=query, fields="files(id,name)").execute()
    return [archivo for archivo in respuesta.get("files", []) if _es_imagen(archivo["name"])]


def _buscar_visita(fecha: str, lugar: str, cliente) -> int | None:
    """Busca la visita más reciente por fecha y lugar."""
    id_lugar = _buscar_lugar(lugar, cliente)
    if id_lugar is None:
        return None
    consulta = cliente.table("visitas").select("id_visita").eq("fecha", fecha).eq("id_lugar", id_lugar)
    respuesta = consulta.order("id_visita", desc=True).limit(1).execute()
    filas = getattr(respuesta, "data", None) or []
    return filas[0]["id_visita"] if filas else None


def _buscar_lugar(lugar: str, cliente) -> int | None:
    """Busca el id_lugar por nombre_lugar."""
    respuesta = cliente.table("lugares").select("id_lugar").eq("nombre_lugar", lugar).limit(1).execute()
    filas = getattr(respuesta, "data", None) or []
    return filas[0]["id_lugar"] if filas else None


def _foto_existe(url: str, cliente) -> bool:
    """Comprueba si una URL ya está registrada."""
    respuesta = cliente.table("fotos").select("url_drive").eq("url_drive", url).limit(1).execute()
    return bool(getattr(respuesta, "data", None) or [])


def _insertar_foto(id_visita: int, url: str, cliente) -> None:
    """Inserta una foto vinculada a una visita."""
    fila = {"id_visita": id_visita, "url_drive": url, "descripcion": "", "fecha_subida": date.today().isoformat()}
    cliente.table("fotos").insert(fila).execute()


def _url_drive(file_id: str) -> str:
    """Construye la URL pública de visualización de Drive."""
    return f"https://drive.google.com/file/d/{file_id}/view"


def _es_imagen(nombre: str) -> bool:
    """Indica si el archivo tiene extensión de imagen soportada."""
    return any(nombre.lower().endswith(extension) for extension in EXTENSIONES_IMAGEN)


def _aviso(carpeta: dict, mensaje: str) -> dict:
    """Devuelve un resumen de aviso sin interrumpir el proceso."""
    return {"carpeta": carpeta["name"], "estado": "aviso", "mensaje": mensaje}
