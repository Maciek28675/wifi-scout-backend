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
