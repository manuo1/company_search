"""Calcul de distance à vol d'oiseau (formule de Haversine), traduit en SQL
pour être exécuté directement par DuckDB sans charger de données en Python.
"""

EARTH_RADIUS_KM = 6371.0


def haversine_km_sql(lat_col: str, lon_col: str, ref_lat: float, ref_lon: float) -> str:
    """Construit une expression SQL DuckDB calculant la distance en km
    entre (lat_col, lon_col) et un point de référence (ref_lat, ref_lon).
    """
    return f"""
        {EARTH_RADIUS_KM} * 2 * asin(sqrt(
            pow(sin(radians({ref_lat} - {lat_col}) / 2), 2) +
            cos(radians({lat_col})) * cos(radians({ref_lat})) *
            pow(sin(radians({ref_lon} - {lon_col}) / 2), 2)
        ))
    """
