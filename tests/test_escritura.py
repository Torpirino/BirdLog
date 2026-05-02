"""Tests de inserción con mocks, sin base de datos real."""

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.insercion.escritura import insertar_registro
from src.parser.plaud import parsear_txt_plaud

EJEMPLOS = Path(__file__).parent / "ejemplos_plaud"


class Respuesta:
    """Respuesta mínima compatible con supabase-py."""

    def __init__(self, data):
        self.data = data


class TablaFalsa:
    """Simula una tabla Supabase encadenable."""

    def __init__(self, cliente, nombre):
        self.cliente = cliente
        self.nombre = nombre
        self.filtros = []
        self.operacion = "select"
        self.payload = None
        self.columnas = "*"

    def select(self, columnas):
        self.columnas = columnas
        return self

    def eq(self, campo, valor):
        self.filtros.append((campo, valor))
        return self

    def is_(self, campo, valor):
        self.filtros.append((campo, None if valor == "null" else valor))
        return self

    def limit(self, _cantidad):
        return self

    def insert(self, payload):
        self.operacion = "insert"
        self.payload = payload
        return self

    def update(self, payload):
        self.operacion = "update"
        self.payload = payload
        return self

    def execute(self):
        if self.operacion == "insert":
            return self._insertar()
        if self.operacion == "update":
            return self._actualizar()
        return Respuesta(self._seleccionar())

    def _seleccionar(self):
        filas = self.cliente.datos.get(self.nombre, [])
        for campo, valor in self.filtros:
            filas = [fila for fila in filas if fila.get(campo) == valor]
        if self.columnas == "*":
            return filas
        return [{self.columnas: fila[self.columnas]} for fila in filas]

    def _insertar(self):
        filas = self.payload if isinstance(self.payload, list) else [self.payload]
        guardadas = []
        for fila in filas:
            guardada = dict(fila)
            self.cliente.contadores[self.nombre] = self.cliente.contadores.get(self.nombre, 0) + 1
            campo_id = self.cliente.ids.get(self.nombre)
            if campo_id:
                guardada[campo_id] = self.cliente.contadores[self.nombre]
            self.cliente.datos.setdefault(self.nombre, []).append(guardada)
            guardadas.append(guardada)
        return Respuesta(guardadas)

    def _actualizar(self):
        filas = self.cliente.datos.get(self.nombre, [])
        actualizadas = []
        for fila in filas:
            if all(fila.get(campo) == valor for campo, valor in self.filtros):
                fila.update(self.payload)
                actualizadas.append(fila)
        return Respuesta(actualizadas)


class ClienteFalso:
    """Cliente Supabase en memoria para escritura."""

    ids = {"visitas": "id_visita", "meteorologia": "id_meteo", "lindus": "id_lindus", "cajas_nido": "id_cajanido"}

    def __init__(self):
        self.contadores = {"visitas": 100, "meteorologia": 200, "lindus": 300, "cajas_nido": 400}
        self.datos = {
            "lugares": [{"id_lugar": 1, "nombre_lugar": "BAR01"}, {"id_lugar": 2, "nombre_lugar": "Lindus"}],
            "observadores": [{"id_observador": 7, "nombre_observador": "Gabi"}],
            "especies": [
                {"id_especie": 11, "nombre_comun": "carbonero común", "nombre_cientifico": "Parus major"},
                {"id_especie": 12, "nombre_comun": "milano negro", "nombre_cientifico": "Milvus migrans"},
                {"id_especie": 13, "nombre_comun": "milano real", "nombre_cientifico": "Milvus milvus"},
            ],
            "visitas": [{"id_visita": 50, "tipo_visita": "LINDUS", "fecha": "2026-05-01", "hora_fin": None}],
        }

    def table(self, nombre):
        return TablaFalsa(self, nombre)


def test_insertar_visita_caja_nido_crea_visita_meteo_y_dato():
    """Inserta una visita de caja nido completa."""
    cliente = ClienteFalso()
    registro = parsear_txt_plaud(str(EJEMPLOS / "visita_caja_nido_ok.txt"))
    resumen = insertar_registro(registro, cliente)
    caja = cliente.datos["cajas_nido"][0]
    assert resumen["id_visita"] == 101
    assert resumen["insertados"] == {"cajas_nido": 1}
    assert cliente.datos["visitas"][-1]["id_lugar"] == 1
    assert cliente.datos["meteorologia"][0]["hora"] == "12:05"
    assert caja["id_especie"] == 11
    assert "especie" not in caja


def test_insertar_observaciones_lindus_usa_visita_abierta():
    """Inserta observaciones en la visita Lindus abierta del día."""
    cliente = ClienteFalso()
    registro = parsear_txt_plaud(str(EJEMPLOS / "observaciones_lindus_ok.txt"))
    resumen = insertar_registro(registro, cliente)
    assert resumen["id_visita"] == 50
    assert resumen["insertados"] == {"lindus": 2}
    assert [fila["id_especie"] for fila in cliente.datos["lindus"]] == [12, 13]


def test_insertar_observaciones_lindus_falla_sin_visita_abierta():
    """No inserta Lindus si no existe visita abierta."""
    cliente = ClienteFalso()
    cliente.datos["visitas"] = []
    registro = parsear_txt_plaud(str(EJEMPLOS / "observaciones_lindus_ok.txt"))
    with pytest.raises(ValueError, match="No hay visita Lindus abierta"):
        insertar_registro(registro, cliente)


def test_insertar_caja_no_crea_visita_si_falta_especie():
    """Resuelve FKs antes de insertar para no dejar visitas huérfanas."""
    cliente = ClienteFalso()
    cliente.datos["especies"] = []
    registro = parsear_txt_plaud(str(EJEMPLOS / "visita_caja_nido_ok.txt"))
    visitas_antes = list(cliente.datos["visitas"])
    with pytest.raises(ValueError, match="Especie no encontrada"):
        insertar_registro(registro, cliente)
    assert cliente.datos["visitas"] == visitas_antes
    assert "cajas_nido" not in cliente.datos


def test_insertar_mamiferos_puente_no_descarta_observaciones_puente():
    """observaciones_puente llega a visitas.observaciones combinada con observaciones_visita."""
    cliente = ClienteFalso()
    cliente.datos["lugares"].append({"id_lugar": 3, "nombre_lugar": "Puente Prueba 1"})
    cliente.datos["especies"] += [
        {"id_especie": 20, "nombre_comun": "nutria", "nombre_cientifico": "Nutria"},
        {"id_especie": 21, "nombre_comun": "garduña", "nombre_cientifico": "Garduña"},
    ]
    registro = parsear_txt_plaud(str(EJEMPLOS / "visita_mamiferos_puente_ok.txt"))
    insertar_registro(registro, cliente)
    obs = cliente.datos["visitas"][-1].get("observaciones") or ""
    assert "barro reciente en ambas orillas" in obs
    assert "prospección tras lluvia" in obs
