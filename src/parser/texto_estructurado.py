"""Parsea archivos TXT con estructura CAMPO: valor."""

TIPOS_REGISTRO = {
    "INICIO_VISITA_LINDUS",
    "OBSERVACIONES_LINDUS",
    "FIN_VISITA_LINDUS",
    "VISITA_CAJA_NIDO",
    "VISITA_CEBO_AVISPON",
    "VISITA_NIDO_RAPAZ",
    "VISITA_MAMIFEROS_PUENTE",
}

CAMPOS_ENTEROS = {
    "numero",
    "numero_huevos",
    "numero_pollos",
    "pollos_volados",
    "nubosidad",
    "vv",
    "crabro",
    "avispa_europea",
    "polilla",
    "mariposa",
    "otros",
    "presentes",
    "observando",
    "visitantes",
    "utm_x_nido",
    "utm_y_nido",
    "distancia_rio",
    "distancia_peatonal",
    "distancia_carretera",
    "cobertura_vegetal",
    "cobertura_arboles",
    "cobertura_matorral",
    "cobertura_pastizal",
}
CAMPOS_FLOAT = {"temperatura", "peso_pollos", "longitud_tarso"}
CAMPOS_BOOLEANOS = {"ocupada", "incuba"}
PARSERS = {}


def parsear_txt_estructurado(ruta: str) -> dict:
    """Lee un TXT estructurado CAMPO: valor y devuelve su registro."""
    with open(ruta, encoding="utf-8") as archivo:
        texto_original = archivo.read()
    texto = _texto_parseable(texto_original)
    tipo = detectar_tipo(texto)
    registro = PARSERS[tipo](texto)
    registro["_advertencias"] = detectar_advertencias_estructura(texto_original)
    return registro



def detectar_tipo(texto: str) -> str:
    """Extrae TIPO_REGISTRO y comprueba que sea un tipo activo."""
    for clave, valor in _pares_clave_valor(_texto_parseable(texto)):
        if clave == "tipo_registro":
            if valor in TIPOS_REGISTRO:
                return valor
            raise ValueError(f"TIPO_REGISTRO no reconocido: {valor}")
    raise ValueError("TIPO_REGISTRO ausente")


def _texto_parseable(texto: str) -> str:
    """Extrae la salida estructurada si el archivo contiene una plantilla completa."""
    marcador_ejemplo = "EJEMPLO DE SALIDA CORRECTA:"
    marcadores_fin = (
        "EJEMPLO DE SALIDA SI",
        "VALIDACIÓN FINAL ANTES DE RESPONDER:",
    )
    if marcador_ejemplo in texto:
        texto = texto.split(marcador_ejemplo, 1)[1]
    for marcador in marcadores_fin:
        if marcador in texto:
            texto = texto.split(marcador, 1)[0]
    return texto


def detectar_advertencias_estructura(texto: str) -> list[str]:
    """Detecta líneas narrativas previas al primer TIPO_REGISTRO."""
    advertencias = []
    for linea in _lineas_utiles(texto):
        if _es_tipo_registro(linea):
            break
        if ":" not in linea and not _nombre_bloque(linea):
            advertencias.append("Se ignoró texto antes de TIPO_REGISTRO.")
            break
    return advertencias


def parsear_inicio_visita_lindus(texto: str) -> dict:
    """Parsea una apertura de visita Lindus."""
    return _parsear(texto, {})


def parsear_observaciones_lindus(texto: str) -> dict:
    """Parsea bloques de observaciones Lindus."""
    return _parsear(texto, {"OBSERVACION_LINDUS": "datos"})


def parsear_fin_visita_lindus(texto: str) -> dict:
    """Parsea un cierre de visita Lindus con meteorología."""
    return _parsear(texto, {"METEOROLOGIA": "meteorologia"})


def parsear_visita_caja_nido(texto: str) -> dict:
    """Parsea una visita de revisión de caja nido."""
    return _parsear(texto, {"METEOROLOGIA": "meteorologia", "CAJA_NIDO": "datos"})


def parsear_visita_cebo_avispon(texto: str) -> dict:
    """Parsea una visita de revisión de cebo de avispón."""
    return _parsear(texto, {"METEOROLOGIA": "meteorologia", "CEBO_AVISPON": "datos"})


def parsear_visita_nido_rapaz(texto: str) -> dict:
    """Parsea una visita de revisión de nido de rapaz."""
    return _parsear(texto, {"METEOROLOGIA": "meteorologia", "NIDO_RAPAZ": "datos"})


def parsear_visita_mamiferos_puente(texto: str) -> dict:
    """Parsea una visita de mamíferos en puente."""
    bloques = {"METEOROLOGIA": "meteorologia", "MAMIFERO_PUENTE": "datos"}
    return _parsear(texto, bloques)


def _parsear(texto: str, bloques: dict[str, str]) -> dict:
    """Recorre líneas y asigna campos a cabecera o bloques."""
    registro = {"tipo_registro": "", "visita": {}, "meteorologia": [], "datos": []}
    destino = registro["visita"]
    for linea in _lineas_utiles(texto):
        bloque = _nombre_bloque(linea)
        if bloque:
            destino = _abrir_bloque(registro, bloques, bloque)
            continue
        if ":" not in linea:
            continue
        clave, valor = _parsear_linea(linea)
        if valor == "":
            continue
        if clave == "tipo_registro":
            registro["tipo_registro"] = valor
        else:
            destino[clave] = _convertir_valor(clave, valor)
    _limpiar_bloques_vacios(registro)
    return registro


def _abrir_bloque(registro: dict, bloques: dict[str, str], bloque: str) -> dict:
    """Crea un nuevo dict de bloque si el marcador es conocido."""
    lista = bloques.get(bloque)
    if not lista:
        return registro["visita"]
    registro[lista].append({})
    return registro[lista][-1]


def _lineas_utiles(texto: str) -> list[str]:
    """Devuelve líneas con contenido y sin comentarios."""
    return [linea.strip() for linea in texto.splitlines() if _es_linea_util(linea)]


def _es_linea_util(linea: str) -> bool:
    """Indica si una línea participa en el parseo."""
    limpia = linea.strip()
    return bool(limpia) and not limpia.startswith("#")


def _pares_clave_valor(texto: str) -> list[tuple[str, str]]:
    """Extrae pares clave-valor de todas las líneas válidas."""
    return [_parsear_linea(linea) for linea in _lineas_utiles(texto) if ":" in linea]


def _parsear_linea(linea: str) -> tuple[str, str]:
    """Convierte una línea CLAVE: valor en clave snake_case y valor."""
    clave, valor = linea.split(":", 1)
    return _a_snake_case(clave), valor.strip()


def _es_tipo_registro(linea: str) -> bool:
    """Indica si una línea contiene TIPO_REGISTRO."""
    if ":" not in linea:
        return False
    clave, _valor = _parsear_linea(linea)
    return clave == "tipo_registro"


def _a_snake_case(clave: str) -> str:
    """Convierte claves a snake_case minúscula."""
    return clave.strip().lower().replace(" ", "_")


def _nombre_bloque(linea: str) -> str:
    """Obtiene el nombre de un marcador de bloque."""
    if linea.startswith("---") and linea.endswith("---"):
        return linea.strip("-").strip()
    return ""


def _convertir_valor(clave: str, valor: str):
    """Convierte tipos simples sin tocar textos libres."""
    if clave in CAMPOS_ENTEROS:
        return _convertir_numero(clave, valor, int, "un número entero")
    if clave in CAMPOS_FLOAT:
        return _convertir_numero(clave, valor, float, "un número")
    if clave in CAMPOS_BOOLEANOS and valor.lower() in {"true", "false"}:
        return valor.lower() == "true"
    return valor


def _convertir_numero(clave: str, valor: str, conversor, descripcion: str):
    """Convierte un valor numérico con mensaje claro si no es válido."""
    try:
        return conversor(valor)
    except ValueError:
        raise ValueError(
            f"El campo {clave.upper()} recibió '{valor}' y debe ser {descripcion}."
        ) from None


def _limpiar_bloques_vacios(registro: dict) -> None:
    """Descarta bloques de plantilla que no contienen ningún campo."""
    registro["meteorologia"] = [bloque for bloque in registro["meteorologia"] if bloque]
    registro["datos"] = [bloque for bloque in registro["datos"] if bloque]


PARSERS.update(
    {
        "INICIO_VISITA_LINDUS": parsear_inicio_visita_lindus,
        "OBSERVACIONES_LINDUS": parsear_observaciones_lindus,
        "FIN_VISITA_LINDUS": parsear_fin_visita_lindus,
        "VISITA_CAJA_NIDO": parsear_visita_caja_nido,
        "VISITA_CEBO_AVISPON": parsear_visita_cebo_avispon,
        "VISITA_NIDO_RAPAZ": parsear_visita_nido_rapaz,
        "VISITA_MAMIFEROS_PUENTE": parsear_visita_mamiferos_puente,
    }
)
