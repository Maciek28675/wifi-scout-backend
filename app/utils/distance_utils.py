import math


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Oblicz odległość między dwoma punktami.

    Zwraca odległość w metrach.
    """
    # Zamiana stopni na radiany
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))

    # Promień Ziemi w metrach
    r = 6371000

    return c * r


def generate_simple_zone_id(
    lat: float, lon: float, zone_size_meters: float = 100.0
) -> str:
    """
    Wygeneruj prosty identyfikator strefy na podstawie współrzędnych.

    Args:
    - lat: Szerokość geograficzna
    - lon: Długość geograficzna
    - zone_size_meters: Rozmiar strefy w metrach

    Returns:
        str: Identyfikator strefy w formacie "zone_lat_lon"
    """
    lat_cell_size = zone_size_meters / 111320
    lon_cell_size = zone_size_meters / (111320 * math.cos(math.radians(lat)))

    lat_cell = int(lat / lat_cell_size)
    lon_cell = int(lon / lon_cell_size)

    return f"zone_{lat_cell}_{lon_cell}"


def generate_simple_geohash(lat: float, lon: float, precision: int = 7) -> str:
    """
    Wygeneruj geohash na podstawie współrzędnych.
    """
    import hashlib

    lat_str = f"{lat:.{precision}f}"
    lon_str = f"{lon:.{precision}f}"
    combined = f"{lat_str},{lon_str}"
    return hashlib.md5(combined.encode()).hexdigest()[:8]


def find_points_within_radius(
    center_lat: float, center_lon: float, points: list, radius_meters: float
) -> list:
    """
    Znajdź punkty w promieniu od danego punktu.
    """
    nearby_points = []

    for point in points:
        lat, lon = point[0], point[1]
        distance = haversine_distance(center_lat, center_lon, lat, lon)

        if distance <= radius_meters:
            nearby_points.append({"point": point, "distance": distance})

    nearby_points.sort(key=lambda x: x["distance"])
    return nearby_points
