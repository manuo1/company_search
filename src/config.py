import unicodedata
from datetime import date
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

# --- Point de référence et filtres (config personnelle, voir config_local.py) ---
HOME_NAME = local.HOME_NAME
HOME_LAT = local.HOME_LAT
HOME_LON = local.HOME_LON
MAX_DISTANCE_KM = local.MAX_DISTANCE_KM
SEUIL_MIN_EFFECTIF = local.SEUIL_MIN_EFFECTIF


def _slugify(texte: str) -> str:
    """Simplifie une chaîne pour en faire un nom de fichier sûr :
    accents retirés, espaces/caractères spéciaux remplacés par '_'.
    """
    sans_accents = (
        unicodedata.normalize("NFKD", texte)
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    return "".join(c if c.isalnum() else "_" for c in sans_accents).strip("_")


def _nom_fichier_output() -> str:
    """Construit un nom de fichier reflétant les critères de recherche et
    la date de génération, ex :
    entreprises_Chateauneuf_sur_Cher_50km_eff50_2026-07-25.csv
    """
    lieu = _slugify(HOME_NAME)
    aujourdhui = date.today().isoformat()
    return (
        f"entreprises_{lieu}_{MAX_DISTANCE_KM}km_"
        f"eff{SEUIL_MIN_EFFECTIF}_{aujourdhui}.csv"
    )


OUTPUT_FILE = OUTPUT_DIR / _nom_fichier_output()
