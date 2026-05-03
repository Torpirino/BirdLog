#!/bin/bash
# Arranca la app pipeline de BirdLog en el puerto 8502.
# Uso: bash scripts/abrir_app_pipeline.sh

PROYECTO="$HOME/Documentos/BirdLog"

# Título de la ventana de terminal
echo -ne "\033]0;BirdLog — Pipeline Plaud\007"
echo ""
echo "========================================="
echo "  BirdLog — Pipeline Plaud  (puerto 8502)"
echo "========================================="
echo ""

if [ ! -d "$PROYECTO/.venv" ]; then
    echo "ERROR: No se encontró el entorno virtual en:"
    echo "  $PROYECTO/.venv"
    echo ""
    echo "Créalo con:"
    echo "  cd $PROYECTO"
    echo "  python3 -m venv .venv"
    echo "  .venv/bin/pip install streamlit"
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
    echo "Instálalo con:"
    echo "  cd $PROYECTO"
    echo "  .venv/bin/pip install streamlit"
    echo ""
    read -rp "Pulsa Enter para cerrar..."
    exit 1
fi

echo "Arrancando en http://localhost:8502"
echo "El navegador se abrirá automáticamente."
echo "Cierra esta ventana para detener la app."
echo ""

streamlit run app_pipeline/app.py --server.port 8502
