"""Vérifications des fichiers sources Sirene avant de lancer une recherche.

Chaque échec est signalé avec l'action corrective précise à faire (où
télécharger, quel bouton chercher, comment renommer/placer le fichier),
en cohérence avec les instructions du README.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import duckdb

from . import config

# Au-delà de ce nombre de jours, on avertit (sans bloquer) que les
# fichiers sont probablement dépassés (exports Insee mensuels).
JOURS_AVANT_ALERTE_FRAICHEUR = 45


class DonneesInvalides(Exception):
    """Fichier source absent, corrompu ou incomplet.

    Le message est toujours actionnable : il dit quoi faire pour corriger.
    """


@dataclass
class FichierAttendu:
    path: Path
    url_dataset: str
    libelle_bouton: str
    colonnes_attendues: list[str] = field(default_factory=list)


FICHIERS_ATTENDUS = [
    FichierAttendu(
        path=config.ETABLISSEMENT_FILE,
        url_dataset=(
            "https://www.data.gouv.fr/datasets/"
            "base-sirene-des-entreprises-et-de-leurs-etablissements-siren-siret"
        ),
        libelle_bouton=(
            '"Sirene : Fichier StockEtablissement - [date] (format parquet)" '
            '(le stock COURANT, pas "StockEtablissementHistorique")'
        ),
        colonnes_attendues=[
            "siret",
            "siren",
            "etatAdministratifEtablissement",
            "trancheEffectifsEtablissement",
            "enseigne1Etablissement",
            "numeroVoieEtablissement",
            "typeVoieEtablissement",
            "libelleVoieEtablissement",
            "codePostalEtablissement",
            "libelleCommuneEtablissement",
            "activitePrincipaleEtablissement",
        ],
    ),
    FichierAttendu(
        path=config.UNITE_LEGALE_FILE,
        url_dataset=(
            "https://www.data.gouv.fr/datasets/"
            "base-sirene-des-entreprises-et-de-leurs-etablissements-siren-siret"
        ),
        libelle_bouton='"Sirene : Fichier StockUniteLegale - [date] (format parquet)"',
        colonnes_attendues=["siren", "denominationUniteLegale"],
    ),
    FichierAttendu(
        path=config.GEOLOC_FILE,
        url_dataset=(
            "https://www.data.gouv.fr/datasets/"
            "geolocalisation-des-etablissements-du-repertoire-sirene-pour-les-etudes-statistiques"
        ),
        libelle_bouton='"Sirene : Fichier géolocalisation établissements - [date] (format parquet)"',
        colonnes_attendues=["siret", "x_longitude", "y_latitude"],
    ),
]


def _verifier_presence(f: FichierAttendu) -> None:
    if not f.path.exists():
        raise DonneesInvalides(
            f"Fichier manquant : {f.path.name}\n"
            f"  Pour corriger :\n"
            f"  1. Ouvrir {f.url_dataset}\n"
            f"  2. Télécharger le bouton : {f.libelle_bouton}\n"
            f"  3. Renommer le fichier téléchargé exactement en : {f.path.name}\n"
            f"  4. Le placer dans : {f.path.parent}"
        )


def _verifier_signature_parquet(f: FichierAttendu) -> None:
    """Un fichier parquet valide commence et finit par les 4 octets
    magiques 'PAR1'. Détecte un téléchargement tronqué/interrompu ou un
    fichier qui n'est en fait pas au format parquet.
    """
    with open(f.path, "rb") as fh:
        debut = fh.read(4)
        fh.seek(-4, 2)
        fin = fh.read(4)
    if debut != b"PAR1" or fin != b"PAR1":
        raise DonneesInvalides(
            f"Fichier invalide (signature parquet absente) : {f.path.name}\n"
            f"  Cause probable : téléchargement interrompu/corrompu, ou fichier\n"
            f"  qui n'est pas au format parquet (ex. CSV/ZIP renommé en .parquet).\n"
            f"  Pour corriger :\n"
            f"  1. Supprimer {f.path.name}\n"
            f"  2. Re-télécharger depuis {f.url_dataset}\n"
            f"  3. Bouton à chercher : {f.libelle_bouton}\n"
            f"  4. Renommer exactement en : {f.path.name}"
        )


def _verifier_colonnes(f: FichierAttendu, con: duckdb.DuckDBPyConnection) -> None:
    colonnes_reelles = {
        row[0]
        for row in con.execute(
            f"DESCRIBE SELECT * FROM read_parquet('{f.path.as_posix()}') LIMIT 0"
        ).fetchall()
    }
    manquantes = [c for c in f.colonnes_attendues if c not in colonnes_reelles]
    if manquantes:
        raise DonneesInvalides(
            f"Colonnes manquantes dans {f.path.name} : {', '.join(manquantes)}\n"
            f"  Cause probable : mauvais fichier téléchargé (dataset différent,\n"
            f"  fichier historique au lieu du stock courant, ou changement de\n"
            f"  schéma côté Insee).\n"
            f"  Pour corriger :\n"
            f"  1. Vérifier le dataset : {f.url_dataset}\n"
            f"  2. Bouton à chercher : {f.libelle_bouton}\n"
            f"  3. Re-télécharger et renommer exactement en : {f.path.name}"
        )


def _alerte_fraicheur(f: FichierAttendu) -> str | None:
    age_jours = (datetime.now() - datetime.fromtimestamp(f.path.stat().st_mtime)).days
    if age_jours > JOURS_AVANT_ALERTE_FRAICHEUR:
        return (
            f"{f.path.name} date de {age_jours} jours (mise à jour mensuelle "
            f"par l'Insee). Pour des résultats à jour : re-télécharger depuis "
            f"{f.url_dataset}"
        )
    return None


def verifier_donnees() -> None:
    """Vérifie présence, format et contenu des 3 fichiers Sirene attendus.

    Lève DonneesInvalides (message actionnable) au premier problème
    bloquant trouvé. Affiche un avertissement non bloquant si un fichier
    semble dépassé.
    """
    con = duckdb.connect()
    try:
        avertissements = []
        for f in FICHIERS_ATTENDUS:
            _verifier_presence(f)
            _verifier_signature_parquet(f)
            _verifier_colonnes(f, con)
            alerte = _alerte_fraicheur(f)
            if alerte:
                avertissements.append(alerte)
    finally:
        con.close()

    for a in avertissements:
        print(f"[ATTENTION] {a}")
