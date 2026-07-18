# company_search

Recherche d'entreprises autour d'un point de référence, filtrées par
distance à vol d'oiseau et par effectif minimum, à partir des données
publiques Sirene (data.gouv.fr).

Le script croise trois jeux de données Sirene (géolocalisation,
établissements, unités légales) via DuckDB, sans jamais charger
l'ensemble des fichiers en mémoire, et exporte un CSV des entreprises
correspondant aux critères choisis.

## Prérequis

- Python 3.11+
- Un environnement virtuel (`venv`) recommandé

```bash
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

## 1. Récupérer les données Sirene

Les fichiers sources ne sont **pas** versionnés dans ce dépôt (trop
volumineux, mis à jour mensuellement par l'Insee). Il faut les
télécharger manuellement dans `data_from_data.gouv/`.

Format à choisir systématiquement : **parquet** (disponible depuis
juin 2025 sur data.gouv.fr, plus léger et plus rapide à requêter que
le CSV/ZIP).

| Fichier attendu | Où le télécharger | Nom du bouton de téléchargement sur la page |
|---|---|---|
| `stock-stocketablissement-parquet.parquet` | [Base Sirene des entreprises et de leurs établissements](https://www.data.gouv.fr/datasets/base-sirene-des-entreprises-et-de-leurs-etablissements-siren-siret) | *"Sirene : Fichier StockEtablissement - [date] (format parquet)"* — attention à bien prendre le stock **courant**, pas "StockEtablissementHistorique" |
| `stock-stockunitelegale-parquet.parquet` | [Base Sirene des entreprises et de leurs établissements](https://www.data.gouv.fr/datasets/base-sirene-des-entreprises-et-de-leurs-etablissements-siren-siret) | *"Sirene : Fichier StockUniteLegale - [date] (format parquet)"* |
| `geoloc-geolocalisationetablissement-sirene-pour-etudes-statistiques-parquet.parquet` | [Géolocalisation des établissements Sirene](https://www.data.gouv.fr/datasets/geolocalisation-des-etablissements-du-repertoire-sirene-pour-les-etudes-statistiques) | *"Sirene : Fichier géolocalisation établissements - [date] (format parquet)"* |

Marche à suivre pour chaque ligne :
1. Ouvrir le lien de la page dataset.
2. Repérer, parmi les fichiers proposés, celui dont le libellé
   correspond à la colonne "Nom du bouton" (le plus récent disponible).
3. Télécharger, puis **renommer** le fichier téléchargé exactement
   comme indiqué dans la colonne "Fichier attendu" (le nom fourni par
   data.gouv.fr inclut la date et ne correspond pas au nom attendu par
   le script).
4. Placer le fichier renommé dans `data_from_data.gouv/`.

Ces trois fichiers sont mis à jour mensuellement sur data.gouv.fr ;
pour une recherche à jour, re-télécharger périodiquement.

## 2. Configurer votre recherche

La configuration personnelle (point de référence, distance max, seuil
d'effectif) est séparée du code dans `src/config_local.py`, qui n'est
**pas** versionné (il contient votre localisation).

```bash
copy src\config_local.example.py src\config_local.py
```

Puis éditez `src/config_local.py` :

```python
HOME_NAME = "Paris"
HOME_LAT = 48.8566
HOME_LON = 2.3522
MAX_DISTANCE_KM = 50       # à vol d'oiseau
SEUIL_MIN_EFFECTIF = 50    # nombre de salariés minimum
```

## 3. Lancer la recherche

```bash
python main.py
```

Le résultat est écrit dans `output/entreprises_selectionnees.csv`
(non versionné, propre à chaque recherche).

## Structure du projet

```
company_search/
├── data_from_data.gouv/   # fichiers Sirene (non versionnés, voir ci-dessus)
├── output/                # résultats générés (non versionné)
├── src/
│   ├── config.py               # chemins + config personnelle assemblée
│   ├── config_local.py         # config personnelle (non versionné)
│   ├── config_local.example.py # template de config personnelle
│   ├── geo.py                  # calcul de distance (Haversine, en SQL)
│   ├── effectifs.py            # conversion seuil salariés -> codes Insee
│   └── query.py                # construction et exécution de la requête DuckDB
└── main.py
```
