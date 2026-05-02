"""Tests de resolución de catálogos con cliente falso."""

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.insercion.catalogos import resolver_especie, resolver_lugar, resolver_observador


class Respuesta:
    """Respuesta mínima compatible con supabase-py."""

    def __init__(self, data):
        self.data = data


class TablaFalsa:
    """Tabla falsa que permite select/eq/limit/execute."""

    def __init__(self, filas):
        self.filas = filas
        self.filtros = []
        self.columnas = "*"

    def select(self, columnas):
        self.columnas = columnas
        return self

    def eq(self, campo, valor):
        self.filtros.append((campo, valor))
        return self

    def limit(self, _cantidad):
        return self

    def execute(self):
        filas = self.filas
        for campo, valor in self.filtros:
            filas = [fila for fila in filas if fila.get(campo) == valor]
        return Respuesta([{self.columnas: fila[self.columnas]} for fila in filas])


class ClienteFalso:
    """Cliente falso con tablas en memoria."""

    def __init__(self):
        self.tablas = {
            "lugares": [{"id_lugar": 10, "nombre_lugar": "Lindus"}],
            "observadores": [{"id_observador": 2, "nombre_observador": "Gabi"}],
            "especies": [{"id_especie": 5, "nombre_comun": "milano negro", "nombre_cientifico": "Milvus migrans"}],
        }

    def table(self, nombre):
        return TablaFalsa(self.tablas[nombre])


def test_resolver_lugar_devuelve_id():
    """Resuelve un lugar existente por nombre_lugar."""
    assert resolver_lugar("Lindus", ClienteFalso()) == 10


def test_resolver_observador_devuelve_id():
    """Resuelve un observador existente por nombre_observador."""
    assert resolver_observador("Gabi", ClienteFalso()) == 2


def test_resolver_especie_busca_nombre_comun_y_cientifico():
    """Resuelve especies por nombre común y científico."""
    cliente = ClienteFalso()
    assert resolver_especie("milano negro", cliente) == 5
    assert resolver_especie("Milvus migrans", cliente) == 5


def test_resolver_lugar_lanza_error_claro_si_no_existe():
    """Informa cómo corregir un lugar ausente."""
    with pytest.raises(ValueError, match="Lugar no encontrado: 'Trona'"):
        resolver_lugar("Trona", ClienteFalso())


def test_resolver_especie_lanza_error_claro_si_no_existe():
    """Informa cómo corregir una especie ausente."""
    with pytest.raises(ValueError, match="Especie no encontrada: 'nutria'"):
        resolver_especie("nutria", ClienteFalso())


def test_resolver_especie_tolera_minusculas_si_bd_tiene_mayuscula_inicial():
    """Plaud transcribe en minúsculas; la BD guarda con primera letra en mayúscula."""
    cliente = ClienteFalso()
    cliente.tablas["especies"] = [
        {"id_especie": 5, "nombre_comun": "Milano negro", "nombre_cientifico": "Milvus migrans"}
    ]
    assert resolver_especie("milano negro", cliente) == 5
    assert resolver_especie("Milano negro", cliente) == 5


def test_resolver_especie_tolera_minusculas_en_nombre_cientifico():
    """Funciona también si el nombre científico viene en minúsculas."""
    cliente = ClienteFalso()
    cliente.tablas["especies"] = [
        {"id_especie": 7, "nombre_comun": "Milano negro", "nombre_cientifico": "Milvus migrans"}
    ]
    assert resolver_especie("milvus migrans", cliente) == 7
