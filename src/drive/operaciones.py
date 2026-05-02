"""Operaciones básicas sobre archivos de Google Drive."""

from io import BytesIO
from pathlib import Path


def listar_txt(carpeta_id: str, drive) -> list[dict]:
    """Lista archivos TXT directos de una carpeta Drive."""
    query = f"'{carpeta_id}' in parents and mimeType='text/plain' and trashed=false"
    respuesta = drive.files().list(q=query, fields="files(id,name,parents)").execute()
    return respuesta.get("files", [])


def descargar_archivo(archivo_id: str, destino: str | Path, drive) -> Path:
    """Descarga un archivo Drive a una ruta local."""
    ruta = Path(destino)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    request = drive.files().get_media(fileId=archivo_id)
    contenido = _descargar_bytes(request)
    ruta.write_bytes(contenido)
    return ruta


def mover_archivo(archivo: dict, carpeta_destino_id: str, drive) -> None:
    """Mueve un archivo Drive a otra carpeta."""
    padres = ",".join(archivo.get("parents", []))
    drive.files().update(
        fileId=archivo["id"],
        addParents=carpeta_destino_id,
        removeParents=padres,
        fields="id, parents",
    ).execute()


def subir_archivo(ruta: str | Path, carpeta_id: str, drive) -> dict:
    """Sube un archivo local a una carpeta Drive."""
    try:
        from googleapiclient.http import MediaFileUpload
    except ImportError as exc:
        raise RuntimeError("Falta instalar google-api-python-client.") from exc
    ruta = Path(ruta)
    media = MediaFileUpload(str(ruta), resumable=False)
    body = {"name": ruta.name, "parents": [carpeta_id]}
    return drive.files().create(body=body, media_body=media, fields="id,name").execute()


def subir_carpeta_csv(carpeta: str | Path, carpeta_drive_id: str, drive) -> list[dict]:
    """Sube los CSV de una carpeta local a Drive."""
    return [subir_archivo(ruta, carpeta_drive_id, drive) for ruta in Path(carpeta).glob("*.csv")]


def _descargar_bytes(request) -> bytes:
    """Ejecuta una descarga con MediaIoBaseDownload."""
    try:
        from googleapiclient.http import MediaIoBaseDownload
    except ImportError as exc:
        raise RuntimeError("Falta instalar google-api-python-client.") from exc
    buffer = BytesIO()
    descarga = MediaIoBaseDownload(buffer, request)
    terminado = False
    while not terminado:
        _, terminado = descarga.next_chunk()
    return buffer.getvalue()
