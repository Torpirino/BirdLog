#!/bin/bash
# Arranca el dashboard de BirdLog en el puerto 8999.
# Uso: bash scripts/abrir_dashboard.sh

PROYECTO="$HOME/Documentos/BirdLog"
PUERTO="8999"
URL="http://localhost:$PUERTO"
LOCK_DIR="/tmp/birdlog_dashboard_$PUERTO.lock"

echo -ne "\033]0;BirdLog — Dashboard\007"
echo ""
echo "=================================="
echo "  BirdLog — Dashboard  (puerto 8999)"
echo "=================================="
echo ""

if [ ! -d "$PROYECTO/.venv" ]; then
    echo "ERROR: No se encontró el entorno virtual en:"
    echo "  $PROYECTO/.venv"
    echo ""
    read -rp "Pulsa Enter para cerrar..."
    exit 1
fi

cd "$PROYECTO" || {
    echo "ERROR: No se puede acceder a $PROYECTO"
    read -rp "Pulsa Enter para cerrar..."
    exit 1
}

# shellcheck disable=SC1091
source .venv/bin/activate

if ! command -v streamlit &> /dev/null; then
    echo "ERROR: Streamlit no está disponible en el entorno virtual."
    echo ""
    read -rp "Pulsa Enter para cerrar..."
    exit 1
fi

puerto_activo() {
    python3 - "$1" <<'PY'
import socket
import sys

puerto = int(sys.argv[1])
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.settimeout(0.2)
    raise SystemExit(0 if sock.connect_ex(("127.0.0.1", puerto)) == 0 else 1)
PY
}

abrir_navegador() {
    if [ "${BIRDLOG_NO_ABRIR_NAVEGADOR:-}" = "1" ]; then
        return
    fi

    if ! command -v xdg-open &> /dev/null; then
        echo "No se encontró xdg-open. Abre manualmente: $URL"
        return
    fi

    for _ in {1..30}; do
        if puerto_activo "$PUERTO"; then
            xdg-open "$URL" >/dev/null 2>&1 &
            return
        fi
        sleep 0.5
    done

    echo "El dashboard tarda en arrancar. Abre manualmente: $URL"
}

if [ -d "$LOCK_DIR" ]; then
    if puerto_activo "$PUERTO"; then
        echo "BirdLog Dashboard ya está arrancado."
        echo "Abre el navegador en: $URL"
        echo ""
        read -rp "Pulsa Enter para cerrar esta ventana..."
        exit 0
    fi
    rmdir "$LOCK_DIR" 2>/dev/null || true
fi

if ! mkdir "$LOCK_DIR" 2>/dev/null; then
    echo "BirdLog Dashboard ya se está arrancando."
    echo "Espera unos segundos y abre: $URL"
    echo ""
    read -rp "Pulsa Enter para cerrar esta ventana..."
    exit 0
fi

trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

echo "Arrancando en $URL"
if [ "${BIRDLOG_NO_ABRIR_NAVEGADOR:-}" = "1" ]; then
    echo "La app pipeline abrirá el navegador."
else
    echo "El navegador se abrirá automáticamente."
fi
echo "Cierra esta ventana para detener el dashboard."
echo ""

abrir_navegador &
streamlit run dashboard/app.py --server.port "$PUERTO" --server.headless true
