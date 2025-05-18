import math


def calculate_spn(toponym):
    envelope = toponym["boundedBy"]["Envelope"]
    left, bottom = envelope["lowerCorner"].split()
    right, top = envelope["upperCorner"].split()

    dx = abs(float(right) - float(left)) / 2.0
    dy = abs(float(top) - float(bottom)) / 2.0

    return f"{dx},{dy}"


def calculate_center_and_zoom(point1, point2):
    lon1, lat1 = map(float, point1)
    lon2, lat2 = map(float, point2)

    center_lon = (lon1 + lon2) / 2
    center_lat = (lat1 + lat2) / 2

    distance = math.sqrt((lon2 - lon1)**2 + (lat2 - lat1)**2)
    zoom = 12 - min(11, math.log(distance * 100, 2))

    return f"{center_lon},{center_lat}", zoom


def haversine_distance(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * \
        math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))

    return 6371 * c
