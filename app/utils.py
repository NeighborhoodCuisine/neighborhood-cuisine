from math import radians, sqrt, cos, sin, asin


EARTH_RADIUS = 6731000


def distance(first, second, r=EARTH_RADIUS):
    lat1, lon1 = first
    lat2, lon2 = second
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    delta_lat = lat1 - lat2
    delta_lon = radians(lon1) - radians(lon2)
    d = 2 * r * asin(
        sqrt(sin(delta_lat/2) ** 2 +
             cos(lat1) * cos(lat2) *
             sin(delta_lon/2) ** 2)
        )
    return d


def contains(l, e):
    for elem in l:
        if elem in e or e in elem:
            return True
    return False