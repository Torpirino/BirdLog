"""Inserta registros Plaud validados en Supabase."""

from src.diagnosticos import ErrorDetalle, PipelineError
from src.insercion.catalogos import resolver_especie, resolver_lugar, resolver_observador


TIPOS_CON_LUGAR = {
    "INICIO_VISITA_LINDUS": "lugar_visita",
    "VISITA_CAJA_NIDO": "lugar_caja",
    "VISITA_CEBO_AVISPON": "lugar_cebo",
    "VISITA_NIDO_RAPAZ": "lugar_nido",
    "VISITA_MAMIFEROS_PUENTE": "lugar_puente",
}


def insertar_registro(registro: dict, cliente) -> dict:
    """Inserta un registro completo y devuelve un resumen."""
    tipo = registro["tipo_registro"]
    if tipo == "OBSERVACIONES_LINDUS":
        return _insertar_observaciones_lindus(registro, cliente)
    if tipo == "FIN_VISITA_LINDUS":
        return _insertar_fin_lindus(registro, cliente)
    return _insertar_visita_con_datos(registro, cliente)


def _insertar_visita_con_datos(registro: dict, cliente) -> dict:
    """Inserta visita, meteorología y datos asociados."""
    referencias = _resolver_referencias(registro, cliente)
    id_visita, id_lugar = _crear_visita(registro, referencias, cliente)
    _insertar_meteorologia(registro["meteorologia"], id_visita, cliente)
    insertados = _insertar_datos_especificos(registro, referencias, id_visita, id_lugar, cliente)
    return {"tipo_registro": registro["tipo_registro"], "id_visita": id_visita, "insertados": insertados}


def _resolver_referencias(registro: dict, cliente) -> dict:
    """Resuelve todas las FKs antes de insertar nada."""
    visita = registro["visita"]
    tipo = registro["tipo_registro"]
    errores = []
    refs = {
        "id_lugar": _resolver_lugar_seguro(visita[TIPOS_CON_LUGAR[tipo]], TIPOS_CON_LUGAR[tipo], cliente, errores),
        "id_observador": _resolver_observador_seguro(visita["observador"], cliente, errores),
        "ids_especies": _resolver_especies_datos(tipo, registro["datos"], cliente, errores),
    }
    if errores:
        raise PipelineError("<registro>", "catálogo/FK", errores)
    return refs


def _resolver_especies_datos(tipo: str, datos: list[dict], cliente, errores: list[ErrorDetalle]) -> list[int | None]:
    """Resuelve especies requeridas u opcionales de bloques específicos."""
    if tipo in {"VISITA_CAJA_NIDO", "VISITA_NIDO_RAPAZ"}:
        return [_resolver_especie_opcional(datos[0], cliente, errores)]
    if tipo == "VISITA_MAMIFEROS_PUENTE":
        return [_resolver_especie_segura(dato["especie"], "especie", cliente, errores) for dato in datos]
    return []


def _crear_visita(registro: dict, referencias: dict, cliente) -> tuple[int, int]:
    """Crea una fila en visitas y devuelve IDs clave."""
    visita = registro["visita"]
    id_lugar = referencias["id_lugar"]
    id_observador = referencias["id_observador"]
    fila = _fila_visita(visita, id_lugar, id_observador)
    respuesta = cliente.table("visitas").insert(fila).execute()
    return _id_insertado(respuesta, "id_visita"), id_lugar


def _fila_visita(visita: dict, id_lugar: int, id_observador: int) -> dict:
    """Prepara columnas de la tabla visitas."""
    return {
        "id_lugar": id_lugar,
        "id_observador": id_observador,
        "tipo_visita": visita["tipo_visita"],
        "fecha": visita["fecha"],
        "hora_inicio": visita["hora_inicio"],
        "hora_fin": visita.get("hora_fin"),
        "observaciones": _combinar_obs(
            visita.get("observaciones_visita"),
            visita.get("observaciones_puente"),
        ),
    }


def _combinar_obs(principal: str | None, adicional: str | None) -> str | None:
    """Combina observaciones de visita y de punto (puente) sin perder ninguna."""
    partes = [p for p in [principal, adicional] if p]
    return " | ".join(partes) if partes else None


def _insertar_observaciones_lindus(registro: dict, cliente) -> dict:
    """Inserta observaciones en la visita Lindus candidata."""
    id_visita, cerrada = _buscar_visita_lindus_para_observaciones(registro, cliente)
    ids_especies = _resolver_especies_lindus(registro["datos"], cliente)
    filas = [_fila_lindus(dato, id_visita, id_especie) for dato, id_especie in zip(registro["datos"], ids_especies)]
    cliente.table("lindus").insert(filas).execute()
    mensaje = f"Observaciones añadidas a la visita Lindus existente id={id_visita}."
    if cerrada:
        mensaje += " Aviso: la visita ya tenía hora de fin."
    return {
        "tipo_registro": registro["tipo_registro"],
        "id_visita": id_visita,
        "insertados": {"lindus": len(filas)},
        "mensaje": mensaje,
    }


def _insertar_fin_lindus(registro: dict, cliente) -> dict:
    """Cierra una visita Lindus abierta e inserta meteorología."""
    visita = registro["visita"]
    abierta = _buscar_visita_lindus_abierta(visita["fecha"], cliente, "cerrar")
    id_visita = abierta["id_visita"]
    cambios = {"hora_fin": visita["hora_fin"]}
    # Las observaciones del cierre se combinan con las del inicio para no
    # perder ninguna; un cierre sin observaciones no toca el campo.
    if visita.get("observaciones_visita"):
        cambios["observaciones"] = _combinar_obs(
            abierta.get("observaciones"),
            visita["observaciones_visita"],
        )
    cliente.table("visitas").update(cambios).eq("id_visita", id_visita).execute()
    _insertar_meteorologia(registro["meteorologia"], id_visita, cliente)
    return {"tipo_registro": registro["tipo_registro"], "id_visita": id_visita, "insertados": {"meteorologia": len(registro["meteorologia"])}}


def _buscar_visita_lindus_abierta(fecha: str, cliente, accion: str) -> dict:
    """Localiza la visita Lindus abierta para una fecha y devuelve su fila."""
    consulta = cliente.table("visitas").select("id_visita,observaciones").eq("tipo_visita", "LINDUS").eq("fecha", fecha)
    consulta = consulta.is_("hora_fin", "null") if hasattr(consulta, "is_") else consulta.eq("hora_fin", None)
    respuesta = consulta.limit(1).execute()
    filas = getattr(respuesta, "data", None) or []
    if not filas:
        raise ValueError(
            f"No hay visita Lindus abierta para {accion} en la fecha {fecha}. "
            "Procesa primero el archivo INICIO_VISITA_LINDUS de ese día."
        )
    return filas[0]


def _buscar_visita_lindus_para_observaciones(registro: dict, cliente) -> tuple[int, bool]:
    """Busca una única visita Lindus por fecha y filtros opcionales."""
    visita = registro["visita"]
    fecha = visita["fecha"]
    filas = _visitas_lindus_fecha(fecha, cliente)
    filas = _filtrar_lindus_por_lugar(filas, visita, cliente)
    filas = _filtrar_lindus_por_observador(filas, visita, cliente)
    if not filas:
        raise ValueError(
            f"No existe ninguna visita Lindus para la fecha {fecha}. "
            "Procesa primero el archivo INICIO_VISITA_LINDUS."
        )
    if len(filas) > 1:
        raise ValueError(
            f"Hay varias visitas Lindus para la fecha {fecha}. "
            "No se puede saber a cuál añadir las observaciones. "
            "Incluye lugar/observador en el archivo o resuélvelo manualmente."
        )
    fila = filas[0]
    return fila["id_visita"], bool(fila.get("hora_fin"))


def _visitas_lindus_fecha(fecha: str, cliente) -> list[dict]:
    """Devuelve visitas Lindus candidatas de una fecha."""
    respuesta = (
        cliente.table("visitas")
        .select("id_visita,hora_fin,id_lugar,id_observador")
        .eq("tipo_visita", "LINDUS")
        .eq("fecha", fecha)
        .execute()
    )
    return getattr(respuesta, "data", None) or []


def _filtrar_lindus_por_lugar(filas: list[dict], visita: dict, cliente) -> list[dict]:
    """Filtra por lugar si OBSERVACIONES_LINDUS lo incluye en el futuro."""
    if not visita.get("lugar_visita"):
        return filas
    id_lugar = resolver_lugar(visita["lugar_visita"], cliente)
    return [fila for fila in filas if fila.get("id_lugar") == id_lugar]


def _filtrar_lindus_por_observador(filas: list[dict], visita: dict, cliente) -> list[dict]:
    """Filtra por observador si OBSERVACIONES_LINDUS lo incluye en el futuro."""
    if not visita.get("observador"):
        return filas
    id_observador = resolver_observador(visita["observador"], cliente)
    return [fila for fila in filas if fila.get("id_observador") == id_observador]


def _insertar_meteorologia(bloques: list[dict], id_visita: int, cliente) -> None:
    """Inserta bloques de meteorología si existen."""
    if not bloques:
        return
    filas = [_fila_meteo(bloque, id_visita) for bloque in bloques]
    cliente.table("meteorologia").insert(filas).execute()


def _insertar_datos_especificos(registro: dict, referencias: dict, id_visita: int, id_lugar: int, cliente) -> dict:
    """Despacha la inserción de la tabla específica."""
    tipo = registro["tipo_registro"]
    if tipo == "VISITA_CAJA_NIDO":
        return _insertar_caja(registro["datos"][0], referencias["ids_especies"][0], id_visita, id_lugar, cliente)
    if tipo == "VISITA_CEBO_AVISPON":
        return _insertar_cebo(registro["datos"][0], id_visita, id_lugar, cliente)
    if tipo == "VISITA_NIDO_RAPAZ":
        return _insertar_nido(registro["datos"][0], referencias["ids_especies"][0], id_visita, id_lugar, cliente)
    if tipo == "VISITA_MAMIFEROS_PUENTE":
        return _insertar_mamiferos(registro["datos"], referencias["ids_especies"], id_visita, id_lugar, cliente)
    return {}


def _fila_meteo(bloque: dict, id_visita: int) -> dict:
    """Mapea meteorología Plaud a columnas SQL."""
    return {
        "id_visita": id_visita,
        "hora": bloque["hora_meteo"],
        "temperatura": bloque.get("temperatura"),
        "nubosidad": bloque.get("nubosidad"),
        "viento_direccion": bloque.get("viento_direccion"),
        "viento_intensidad": bloque.get("viento_intensidad"),
        "precipitacion": bloque.get("precipitacion"),
        "visibilidad": bloque.get("visibilidad"),
        "presentes": bloque.get("presentes"),
        "observando": bloque.get("observando"),
        "visitantes": bloque.get("visitantes"),
        "observaciones": bloque.get("observaciones_meteo"),
    }


def _fila_lindus(dato: dict, id_visita: int, id_especie: int) -> dict:
    """Mapea observación Lindus a columnas SQL."""
    return {"id_visita": id_visita, "id_especie": id_especie, "hora": dato["hora"], "numero": dato["numero"], "comportamiento": dato["comportamiento"], "edad": dato.get("edad"), "sexo": dato.get("sexo"), "plumaje": dato.get("plumaje"), "observaciones": dato.get("observaciones")}


def _insertar_caja(dato: dict, id_especie: int | None, id_visita: int, id_lugar: int, cliente) -> dict:
    """Inserta una revisión de caja nido."""
    fila = dict(dato)
    fila.pop("especie", None)
    fila.update({"id_visita": id_visita, "id_lugar": id_lugar, "id_especie": id_especie, "observaciones": fila.pop("observaciones_caja", None)})
    cliente.table("cajas_nido").insert(fila).execute()
    return {"cajas_nido": 1}


def _insertar_cebo(dato: dict, id_visita: int, id_lugar: int, cliente) -> dict:
    """Inserta una revisión de cebo de avispón."""
    fila = {
        "id_visita": id_visita,
        "id_lugar": id_lugar,
        "vv": dato.get("vv", 0),
        "crabro": dato.get("crabro"),
        "avispa_europea": dato.get("avispa_europea"),
        "polilla": dato.get("polilla"),
        "mariposa": dato.get("mariposa"),
        "otros": dato.get("otros"),
        "observaciones": dato.get("observaciones_cebo"),
        "numero_trampa": dato.get("numero_trampa"),
        "fecha_colocacion": dato.get("fecha_colocacion"),
        "utm_x_nido": dato.get("utm_x_nido"),
        "utm_y_nido": dato.get("utm_y_nido"),
    }
    cliente.table("cebos_avispones").insert(fila).execute()
    return {"cebos_avispones": 1}


def _insertar_nido(dato: dict, id_especie: int | None, id_visita: int, id_lugar: int, cliente) -> dict:
    """Inserta una revisión de nido de rapaz."""
    fila = {
        "id_visita": id_visita,
        "id_lugar": id_lugar,
        "id_especie": id_especie,
        "texto_revision": dato["texto_revision"],
        "comunicacion_personal": dato.get("comunicacion_personal"),
        "descripcion_nido": dato.get("descripcion_nido"),
        "incuba": dato.get("incuba"),
        "numero_pollos": dato.get("numero_pollos"),
        "pollos_volados": dato.get("pollos_volados"),
        "observaciones": dato.get("observaciones_nido"),
    }
    cliente.table("nidos_rapaces").insert(fila).execute()
    return {"nidos_rapaces": 1}


def _insertar_mamiferos(datos: list[dict], ids_especies: list[int], id_visita: int, id_lugar: int, cliente) -> dict:
    """Inserta detecciones de mamíferos en puente."""
    filas = [{"id_visita": id_visita, "id_lugar": id_lugar, "id_especie": id_especie, "presencia": dato["presencia"], "tipo_evidencia": dato.get("tipo_evidencia"), "observaciones": dato.get("observaciones_mamifero")} for dato, id_especie in zip(datos, ids_especies)]
    cliente.table("mamiferos_puentes").insert(filas).execute()
    return {"mamiferos_puentes": len(filas)}


def _resolver_especie_opcional(dato: dict, cliente, errores: list[ErrorDetalle]) -> int | None:
    """Resuelve especie solo cuando Plaud la incluyó."""
    if not dato.get("especie"):
        return None
    return _resolver_especie_segura(dato["especie"], "especie", cliente, errores)


def _resolver_especies_lindus(datos: list[dict], cliente) -> list[int]:
    """Resuelve especies Lindus antes de insertar filas."""
    errores = []
    ids = [_resolver_especie_segura(dato["especie"], "especie", cliente, errores) for dato in datos]
    if errores:
        raise PipelineError("<registro>", "catálogo/FK", errores)
    return ids


def _resolver_lugar_seguro(nombre: str, campo: str, cliente, errores: list[ErrorDetalle]) -> int | None:
    """Resuelve lugar acumulando error de catálogo si falla."""
    try:
        return resolver_lugar(nombre, cliente)
    except ValueError as exc:
        errores.append(_error_catalogo("lugares", campo, nombre, exc))
        return None


def _resolver_observador_seguro(nombre: str, cliente, errores: list[ErrorDetalle]) -> int | None:
    """Resuelve observador acumulando error de catálogo si falla."""
    try:
        return resolver_observador(nombre, cliente)
    except ValueError as exc:
        errores.append(_error_catalogo("observadores", "observador", nombre, exc))
        return None


def _resolver_especie_segura(nombre: str, campo: str, cliente, errores: list[ErrorDetalle]) -> int | None:
    """Resuelve especie acumulando error de catálogo si falla."""
    try:
        return resolver_especie(nombre, cliente)
    except ValueError as exc:
        errores.append(_error_catalogo("especies", campo, nombre, exc))
        return None


def _error_catalogo(tabla: str, campo: str, valor: str, exc: ValueError) -> ErrorDetalle:
    """Convierte un error de catálogo en diagnóstico estructurado."""
    mensaje = str(exc)
    ambiguo = "ambiguo" in mensaje.lower()
    etiqueta = {"lugares": "lugar", "observadores": "observador", "especies": "especie"}[tabla]
    if ambiguo:
        motivo = f"{etiqueta} ambiguo en catálogo"
    else:
        final = "encontrada" if etiqueta == "especie" else "encontrado"
        motivo = f"{etiqueta} no {final} en catálogo"
    return ErrorDetalle(
        fase="catálogo/FK",
        campo=campo,
        contexto=tabla,
        valor=valor,
        motivo=motivo,
        sugerencia=f"usa el nombre exacto del catálogo de {tabla}",
    )


def _id_insertado(respuesta, campo: str) -> int:
    """Extrae el ID devuelto por Supabase tras insert."""
    filas = getattr(respuesta, "data", None) or []
    if not filas or campo not in filas[0]:
        raise RuntimeError(f"Supabase no devolvió {campo} tras la inserción.")
    return filas[0][campo]
