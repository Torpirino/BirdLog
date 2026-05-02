"""Tests de sincronización de fotos con mocks."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.fotos import sincronizar
from src.fotos.sincronizar import _parsear_nombre_carpeta, sincronizar_fotos


class ConfigFalsa:
    """Configuración mínima para fotos."""

    DRIVE_FOTOS_ID = "root"


class Respuesta:
    """Respuesta mínima de APIs encadenadas."""

    def __init__(self, data=None, files=None):
        self.data = data or []
        self.files = files or []

    def get(self, clave, default=None):
        return self.files if clave == "files" else default


class DriveFalso:
    """Drive falso que devuelve carpetas y archivos por padre."""

    def __init__(self, archivos):
        self.archivos = archivos
        self.query = ""

    def files(self):
        return self

    def list(self, q, fields):
        self.query = q
        return self

    def execute(self):
        padre = self.query.split("'")[1]
        archivos = self.archivos.get(padre, [])
        if "application/vnd.google-apps.folder" in self.query:
            archivos = [archivo for archivo in archivos if archivo.get("mimeType") == "application/vnd.google-apps.folder"]
        return {"files": archivos}


class TablaFalsa:
    """Tabla Supabase falsa con filtros simples."""

    def __init__(self, cliente, nombre):
        self.cliente = cliente
        self.nombre = nombre
        self.filtros = []
        self.desc = False
        self.payload = None
        self.operacion = "select"

    def select(self, _columnas):
        return self

    def eq(self, campo, valor):
        self.filtros.append((campo, valor))
        return self

    def order(self, _campo, desc=False):
        self.desc = desc
        return self

    def limit(self, _cantidad):
        return self

    def insert(self, payload):
        self.operacion = "insert"
        self.payload = payload
        return self

    def execute(self):
        if self.operacion == "insert":
            self.cliente.datos.setdefault(self.nombre, []).append(dict(self.payload))
            return Respuesta(data=[self.payload])
        filas = self._filtrar()
        return Respuesta(data=filas)

    def _filtrar(self):
        filas = list(self.cliente.datos.get(self.nombre, []))
        for campo, valor in self.filtros:
            filas = [fila for fila in filas if fila.get(campo) == valor]
        return sorted(filas, key=lambda fila: fila.get("id_visita", 0), reverse=self.desc)


class ClienteFalso:
    """Cliente Supabase falso para fotos."""

    def __init__(self, fotos=None):
        self.datos = {
            "lugares": [{"id_lugar": 1, "nombre_lugar": "Lindus"}],
            "visitas": [{"id_visita": 5, "fecha": "2026-05-01", "id_lugar": 1}],
            "fotos": fotos or [],
        }

    def table(self, nombre):
        return TablaFalsa(self, nombre)


def test_parsear_nombre_carpeta_valido():
    """Devuelve fecha y lugar para formato válido."""
    assert _parsear_nombre_carpeta("2026-05-01_Lindus") == ("2026-05-01", "Lindus")


def test_parsear_nombre_carpeta_invalido():
    """Devuelve None para formato inválido."""
    assert _parsear_nombre_carpeta("Lindus_2026-05-01") is None


def test_parsear_nombre_carpeta_lugar_con_guiones():
    """Conserva guiones del lugar tras el primer guión bajo."""
    assert _parsear_nombre_carpeta("2026-05-01_Cebo-avispon-3") == ("2026-05-01", "Cebo-avispon-3")


def test_sincronizar_fotos_carpeta_vacia(monkeypatch):
    """Con carpeta raíz sin subcarpetas devuelve lista vacía."""
    monkeypatch.setattr(sincronizar, "cargar_config", lambda: ConfigFalsa())
    monkeypatch.setattr(sincronizar, "get_cliente", lambda: ClienteFalso())
    monkeypatch.setattr(sincronizar, "get_drive", lambda: DriveFalso({"root": []}))
    assert sincronizar_fotos() == []


def test_sincronizar_fotos_no_duplica_foto_existente(monkeypatch):
    """Omite una imagen si su URL ya existe en fotos."""
    url = "https://drive.google.com/file/d/img1/view"
    drive = DriveFalso({"root": [_carpeta("2026-05-01_Lindus", "c1")], "c1": [_imagen("img1", "foto.jpg")]})
    cliente = ClienteFalso(fotos=[{"url_drive": url}])
    monkeypatch.setattr(sincronizar, "cargar_config", lambda: ConfigFalsa())
    monkeypatch.setattr(sincronizar, "get_cliente", lambda: cliente)
    monkeypatch.setattr(sincronizar, "get_drive", lambda: drive)
    assert sincronizar_fotos()[0]["omitidas"] == 1
    assert cliente.datos["fotos"] == [{"url_drive": url}]


def test_sincronizar_fotos_ignora_carpeta_invalida(monkeypatch):
    """Registra aviso para carpetas con nombre inválido."""
    drive = DriveFalso({"root": [_carpeta("Lindus", "c1")]})
    monkeypatch.setattr(sincronizar, "cargar_config", lambda: ConfigFalsa())
    monkeypatch.setattr(sincronizar, "get_cliente", lambda: ClienteFalso())
    monkeypatch.setattr(sincronizar, "get_drive", lambda: drive)
    resultado = sincronizar_fotos()
    assert resultado[0]["estado"] == "aviso"


def _carpeta(nombre, file_id):
    """Crea una carpeta falsa de Drive."""
    return {"id": file_id, "name": nombre, "mimeType": "application/vnd.google-apps.folder"}


def _imagen(file_id, nombre):
    """Crea una imagen falsa de Drive."""
    return {"id": file_id, "name": nombre, "mimeType": "image/jpeg"}
