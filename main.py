import sys

from src import config
from src.data_check import DonneesInvalides, verifier_donnees
from src.query import run_export


def main() -> None:
    try:
        verifier_donnees()
    except DonneesInvalides as erreur:
        print(f"[ERREUR] {erreur}")
        sys.exit(1)

    print(
        f"Recherche des entreprises à moins de {config.MAX_DISTANCE_KM} km "
        f"de {config.HOME_NAME}, effectif >= {config.SEUIL_MIN_EFFECTIF}..."
    )
    run_export()
    print(f"Terminé. Résultat : {config.OUTPUT_FILE}")


if __name__ == "__main__":
    main()
