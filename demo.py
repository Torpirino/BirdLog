#!/usr/bin/env python3
"""Demo del pipeline BirdLog.

Procesa un archivo .txt de Plaud paso a paso:
  parseo → validación → verificación de catálogos → inserción → backup

Uso:
  python demo.py demo/04_cebo_avispon.txt
  python demo.py demo/04_cebo_avispon.txt --dry-run

Con --dry-run se ejecutan todos los pasos de verificación pero NO se
inserta nada en Supabase.

Sin --dry-run se pide confirmación explícita escribiendo INSERTAR antes
de tocar la base de datos.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

_SEP = "─" * 60


def main() -> None:
    args = _argumentos()
    ruta = Path(args.archivo)

    _encabezado(ruta, args.dry_run)
    _verificar_entorno()

    registro = _paso_parseo(ruta)
    cliente = _conectar_supabase()
    _paso_catalogos(registro, cliente)
    _mostrar_resumen(registro)

    if args.dry_run:
        print(f"\n  ✓ DRY-RUN completado. No se ha insertado nada.\n")
        return

    _confirmar_insercion()
    _paso_insercion(ruta, cliente)


# ── argumentos ────────────────────────────────────────────────────────────────

def _argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("archivo", help="Ruta al archivo .txt de Plaud")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Verifica todo sin insertar en Supabase",
    )
    return parser.parse_args()


# ── entorno ───────────────────────────────────────────────────────────────────

def _verificar_entorno() -> None:
    from dotenv import load_dotenv
    import os

    load_dotenv(Path(__file__).resolve().parent / ".env")
    entorno = os.getenv("ENTORNO", "").strip()
    if entorno != "dev":
        _error(
            f"ENTORNO='{entorno}' — la demo solo funciona con ENTORNO=dev.\n"
            "  Comprueba el archivo .env."
        )
    print(f"  ✓ Entorno: {entorno}")


# ── paso 1: parseo y validación ───────────────────────────────────────────────

def _paso_parseo(ruta: Path) -> dict:
    _titulo("1", "Parsear y validar el archivo")

    if not ruta.exists():
        _error(f"Archivo no encontrado: {ruta}")

    from src.parser.normalizacion import normalizar_registro
    from src.parser.plaud import parsear_txt_plaud
    from src.parser.validacion import validar_registro

    try:
        registro = normalizar_registro(parsear_txt_plaud(str(ruta)))
    except Exception as exc:
        _error(f"No se pudo parsear el archivo:\n  {exc}")

    errores = validar_registro(registro)
    if errores:
        print("  ✗ Errores de validación:")
        for e in errores:
            print(f"      • {e}")
        _error("El archivo tiene errores. Corrígelos antes de continuar.")

    tipo = registro["tipo_registro"]
    visita = registro.get("visita", {})
    datos = registro.get("datos", [])
    meteo = registro.get("meteorologia", [])

    print(f"  ✓ Tipo            : {tipo}")
    if visita.get("fecha"):
        print(f"  ✓ Fecha           : {visita['fecha']}")
    if visita.get("hora_inicio"):
        print(f"  ✓ Hora inicio     : {visita['hora_inicio']}")
    if datos:
        print(f"  ✓ Bloques de datos: {len(datos)}")
    if meteo:
        print(f"  ✓ Bloques meteo   : {len(meteo)}")

    return registro


# ── conexión ──────────────────────────────────────────────────────────────────

def _conectar_supabase():
    import os
    from supabase import create_client

    url = os.getenv("SUPABASE_DEV_URL", "")
    key = os.getenv("SUPABASE_DEV_KEY", "")
    if not url or not key:
        _error("Faltan SUPABASE_DEV_URL o SUPABASE_DEV_KEY en el .env.")
    try:
        cliente = create_client(url, key)
        return cliente
    except Exception as exc:
        _error(f"No se pudo conectar a Supabase dev:\n  {exc}")


# ── paso 2: verificar catálogos ───────────────────────────────────────────────

def _paso_catalogos(registro: dict, cliente) -> None:
    _titulo("2", "Verificar catálogos en Supabase dev")

    from src.insercion.catalogos import resolver_especie, resolver_lugar, resolver_observador
    from src.insercion.escritura import TIPOS_CON_LUGAR

    tipo = registro["tipo_registro"]
    visita = registro.get("visita", {})

    if tipo in {"OBSERVACIONES_LINDUS", "FIN_VISITA_LINDUS"}:
        _verificar_visita_lindus_abierta(visita.get("fecha", ""), cliente)
        return

    campo_lugar = TIPOS_CON_LUGAR.get(tipo)
    if campo_lugar:
        nombre = visita.get(campo_lugar, "")
        try:
            id_lugar = resolver_lugar(nombre, cliente)
            print(f"  ✓ Lugar      : '{nombre}' → id_lugar={id_lugar}")
        except ValueError as exc:
            _error(str(exc))

    nombre_obs = visita.get("observador", "")
    if nombre_obs:
        try:
            id_obs = resolver_observador(nombre_obs, cliente)
            print(f"  ✓ Observador : '{nombre_obs}' → id_observador={id_obs}")
        except ValueError as exc:
            _error(str(exc))

    for dato in registro.get("datos", []):
        especie = dato.get("especie")
        if especie:
            try:
                id_esp = resolver_especie(especie, cliente)
                print(f"  ✓ Especie    : '{especie}' → id_especie={id_esp}")
            except ValueError as exc:
                _error(str(exc))


def _verificar_visita_lindus_abierta(fecha: str, cliente) -> None:
    if not fecha:
        print("  ⚠  Sin fecha — no se puede verificar visita Lindus abierta.")
        return
    consulta = (
        cliente.table("visitas")
        .select("id_visita")
        .eq("tipo_visita", "LINDUS")
        .eq("fecha", fecha)
        .is_("hora_fin", "null")
        .limit(1)
    )
    filas = getattr(consulta.execute(), "data", None) or []
    if filas:
        print(f"  ✓ Visita Lindus abierta para {fecha}: id_visita={filas[0]['id_visita']}")
    else:
        _error(
            f"No hay visita Lindus abierta para la fecha {fecha}.\n"
            "  Procesa primero el archivo 01_inicio_lindus.txt de ese día."
        )


# ── resumen ───────────────────────────────────────────────────────────────────

def _mostrar_resumen(registro: dict) -> None:
    _titulo("R", "Resumen — lo que se insertará")

    tipo = registro["tipo_registro"]
    visita = registro.get("visita", {})
    datos = registro.get("datos", [])
    meteo = registro.get("meteorologia", [])

    _etiquetas = {
        "INICIO_VISITA_LINDUS": "crear visita Lindus abierta",
        "OBSERVACIONES_LINDUS": f"insertar {len(datos)} observación/es en visita Lindus abierta",
        "FIN_VISITA_LINDUS": f"cerrar visita Lindus + {len(meteo)} registro/s meteorológico/s",
        "VISITA_CAJA_NIDO": "crear visita + 1 revisión de caja nido",
        "VISITA_CEBO_AVISPON": "crear visita + 1 revisión de cebo avispón",
        "VISITA_NIDO_RAPAZ": "crear visita + 1 revisión de nido rapaz",
        "VISITA_MAMIFEROS_PUENTE": f"crear visita + {len(datos)} detección/es de mamíferos",
    }
    print(f"  Acción     : {_etiquetas.get(tipo, tipo)}")
    if visita.get("fecha"):
        print(f"  Fecha      : {visita['fecha']}")
    if visita.get("hora_inicio"):
        print(f"  Hora inicio: {visita['hora_inicio']}")
    if visita.get("hora_fin"):
        print(f"  Hora fin   : {visita['hora_fin']}")
    if meteo:
        print(f"  Meteo      : {len(meteo)} registro/s")
    if datos:
        for dato in datos:
            especie = dato.get("especie", "")
            if especie:
                print(f"  Especie    : {especie}")
    print()
    print(f"  Backup CSV se generará en: backups/backup_YYYY-MM-DD/")


# ── confirmación ──────────────────────────────────────────────────────────────

def _confirmar_insercion() -> None:
    print()
    print(f"  {'='*58}")
    print(f"  Para insertar en Supabase dev escribe exactamente: INSERTAR")
    print(f"  Para cancelar pulsa Ctrl+C o escribe cualquier otra cosa.")
    print(f"  {'='*58}")
    try:
        respuesta = input("  > ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n  Inserción cancelada.")
        sys.exit(0)
    if respuesta != "INSERTAR":
        print("  Inserción cancelada.")
        sys.exit(0)


# ── paso 3: insertar ──────────────────────────────────────────────────────────

def _paso_insercion(ruta: Path, cliente) -> None:
    _titulo("3", "Insertar en Supabase dev")

    from src.pipeline import procesar_txt_local

    try:
        resumen = procesar_txt_local(str(ruta), cliente)
    except ValueError as exc:
        _error(f"Error de catálogo o validación:\n  {exc}")
    except RuntimeError as exc:
        _error(f"Error de conexión:\n  {exc}")
    except Exception as exc:
        _error(f"Error inesperado:\n  {exc}")

    id_visita = resumen.get("id_visita")
    insertados = resumen.get("insertados", {})
    backup = resumen.get("backup", "")

    print(f"  ✓ Inserción correcta")
    if id_visita:
        print(f"  ✓ id_visita  : {id_visita}")
    for tabla, cantidad in insertados.items():
        print(f"  ✓ {tabla:<20}: {cantidad} registro/s")
    if backup:
        print(f"  ✓ Backup CSV : {backup}")
    print()
    print(f"  Comprueba el resultado en el dashboard:")
    print(f"  streamlit run dashboard/app.py")
    print()


# ── utilidades ────────────────────────────────────────────────────────────────

def _encabezado(ruta: Path, dry_run: bool) -> None:
    print()
    print(_SEP)
    print("  DEMO — Pipeline BirdLog")
    print(_SEP)
    print(f"  Archivo : {ruta.name}")
    if dry_run:
        print(f"  Modo    : DRY-RUN (solo verificación, sin insertar)")
    print()


def _titulo(paso: str, texto: str) -> None:
    print()
    print(f"  ── PASO {paso}: {texto}")
    print(f"  {'·'*50}")


def _error(mensaje: str) -> None:
    print(f"\n  ✗ ERROR: {mensaje}\n")
    sys.exit(1)


if __name__ == "__main__":
    main()
