from pathlib import Path

from . import config_local as local

# --- Chemins ---
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data_from_data.gouv"
OUTPUT_DIR = BASE_DIR / "output"

ETABLISSEMENT_FILE = DATA_DIR / "stock-stocketablissement-parquet.parquet"
UNITE_LEGALE_FILE = DATA_DIR / "stock-stockunitelegale-parquet.parquet"
GEOLOC_FILE = (
    DATA_DIR
    / "geoloc-geolocalisationetablissement-sirene-pour-etudes-statistiques-parquet.parquet"
)

OUTPUT_FILE = OUTPUT_DIR / "entreprises_selectionnees.csv"

# --- Point de référence et filtres (config personnelle, voir config_local.py) ---
HOME_NAME = local.HOME_NAME
HOME_LAT = local.HOME_LAT
HOME_LON = local.HOME_LON
MAX_DISTANCE_KM = local.MAX_DISTANCE_KM
SEUIL_MIN_EFFECTIF = local.SEUIL_MIN_EFFECTIF
