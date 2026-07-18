"""Gestion des tranches d'effectifs Insee.

Les fichiers Sirene ne donnent pas un nombre de salariés exact, mais un CODE
de tranche (ex: "21" = 50 à 99 salariés). Ce module convertit un seuil
"humain" (ex: 50) en la liste des codes à conserver.
"""

# Borne basse (nombre de salariés) de chaque tranche Insee
TRANCHES_EFFECTIF = {
    "00": 0,  # 0 salarié
    "01": 1,  # 1 à 2 salariés
    "02": 3,  # 3 à 5 salariés
    "03": 6,  # 6 à 9 salariés
    "11": 10,  # 10 à 19 salariés
    "12": 20,  # 20 à 49 salariés
    "21": 50,  # 50 à 99 salariés
    "22": 100,  # 100 à 199 salariés
    "31": 200,  # 200 à 249 salariés
    "32": 250,  # 250 à 499 salariés
    "41": 500,  # 500 à 999 salariés
    "42": 1000,  # 1000 à 1999 salariés
    "51": 2000,  # 2000 à 4999 salariés
    "52": 5000,  # 5000 à 9999 salariés
    "53": 10000,  # 10000 salariés et plus
}


def codes_effectif_minimum(seuil: int) -> list[str]:
    """Retourne les codes de tranche Insee dont la borne basse >= seuil."""
    return [code for code, borne in TRANCHES_EFFECTIF.items() if borne >= seuil]
