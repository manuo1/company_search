#!/bin/bash
set -euo pipefail

VENV_DIR="venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "Création du venv..."
    python -m venv "$VENV_DIR"
fi

if [ -f "$VENV_DIR/Scripts/activate" ]; then
    source "$VENV_DIR/Scripts/activate"   # Windows Git Bash / MINGW
else
    source "$VENV_DIR/bin/activate"       # Linux / macOS
fi

# --- Dépendances ---
python -m pip install -q --upgrade pip
pip install -q -r requirements.txt

# --- Config personnelle ---
# src/config_local.py contient la localisation, non versionné (voir .gitignore).
# S'il manque, on le crée depuis le template mais on s'arrête : il faut
# l'éditer avant de lancer une vraie recherche (sinon ça tournerait sur
# les valeurs par défaut du template, ex. Paris).
if [ ! -f "src/config_local.py" ]; then
    cp "src/config_local.example.py" "src/config_local.py"
    echo "[ERREUR] src/config_local.py vient d'être créé depuis le template."
    echo "  -> Éditer src/config_local.py (HOME_NAME, HOME_LAT, HOME_LON,"
    echo "     MAX_DISTANCE_KM, SEUIL_MIN_EFFECTIF) avant de relancer ce script."
    exit 1
fi

mkdir -p output
python main.py
