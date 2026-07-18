"""Construction et exécution de la requête DuckDB : croise géoloc, effectifs
et raison sociale, sans jamais charger les fichiers entiers en mémoire.
"""

import duckdb

from . import config
from .effectifs import codes_effectif_minimum
from .geo import haversine_km_sql


def build_query() -> str:
    distance_expr = haversine_km_sql(
        lat_col="g.y_latitude",
        lon_col="g.x_longitude",
        ref_lat=config.HOME_LAT,
        ref_lon=config.HOME_LON,
    )

    codes = codes_effectif_minimum(config.SEUIL_MIN_EFFECTIF)
    codes_sql = ", ".join(f"'{c}'" for c in codes)

    return f"""
        WITH proches AS (
            SELECT
                g.siret,
                {distance_expr} AS distance_km
            FROM read_parquet('{config.GEOLOC_FILE.as_posix()}') AS g
            WHERE {distance_expr} <= {config.MAX_DISTANCE_KM}
        ),
        etablissements_filtres AS (
            SELECT
                e.siret,
                e.siren,
                e.trancheEffectifsEtablissement,
                e.enseigne1Etablissement,
                e.numeroVoieEtablissement,
                e.typeVoieEtablissement,
                e.libelleVoieEtablissement,
                e.codePostalEtablissement,
                e.libelleCommuneEtablissement,
                e.activitePrincipaleEtablissement
            FROM read_parquet('{config.ETABLISSEMENT_FILE.as_posix()}') AS e
            WHERE e.etatAdministratifEtablissement = 'A'
              AND e.trancheEffectifsEtablissement IN ({codes_sql})
        )
        SELECT
            ef.siret,
            ul.denominationUniteLegale AS nom_entreprise,
            ef.enseigne1Etablissement AS enseigne,
            ef.trancheEffectifsEtablissement AS code_effectif,
            ef.numeroVoieEtablissement AS numero_voie,
            ef.typeVoieEtablissement AS type_voie,
            ef.libelleVoieEtablissement AS libelle_voie,
            ef.codePostalEtablissement AS code_postal,
            ef.libelleCommuneEtablissement AS commune,
            ef.activitePrincipaleEtablissement AS code_naf,
            ROUND(p.distance_km, 1) AS distance_km
        FROM etablissements_filtres AS ef
        JOIN proches AS p ON p.siret = ef.siret
        LEFT JOIN read_parquet('{config.UNITE_LEGALE_FILE.as_posix()}') AS ul
            ON ul.siren = ef.siren
        ORDER BY distance_km ASC
    """


def run_export() -> None:
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    query = build_query()

    # COPY écrit directement sur disque via DuckDB, sans repasser par un
    # DataFrame Python : la RAM ne voit jamais l'ensemble des données.
    copy_query = f"""
        COPY ({query})
        TO '{config.OUTPUT_FILE.as_posix()}'
        (HEADER, DELIMITER ';')
    """
    con = duckdb.connect()
    con.execute(copy_query)
    con.close()
