"""Template de configuration personnelle.

Copiez ce fichier en `config_local.py` (dans le même dossier `src/`) et
adaptez les valeurs à votre cas. `config_local.py` n'est jamais versionné
(voir .gitignore) car il contient votre localisation.
"""

# --- Point de référence ---
HOME_NAME = "Paris"
HOME_LAT = 48.8566
HOME_LON = 2.3522

# Distance max de recherche, À VOL D'OISEAU.
# Ne tient pas compte du réseau routier : la distance réelle par la route
# sera toujours supérieure à cette valeur.
MAX_DISTANCE_KM = 50

# --- Filtre effectif ---
# Seuil minimum de salariés souhaité (nombre réel, pas un code Insee)
SEUIL_MIN_EFFECTIF = 50
