import sys
import requests
from map_utils import calculate_spn, calculate_center_and_zoom, haversine_distance


def geocode_address(address):
    geocoder_api_server = "https://geocode-maps.yandex.ru/1.x/"

    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": address,
        "format": "json",
    }

    response = requests.get(geocoder_api_server, params=geocoder_params)
    if not response.ok:
        raise RuntimeError(f"Ошибка геокодирования: {response.status_code}")

    json_response = response.json()
    features = json_response["response"]["GeoObjectCollection"]["featureMember"]
    if not features:
        raise RuntimeError("Адрес не найден")

    toponym = features[0]["GeoObject"]
    pos = toponym["Point"]["pos"]
    return toponym, pos.split()


def find_nearest_pharmacy(lon, lat):
    search_api_server = "https://search-maps.yandex.ru/v1/"

    search_params = {
        "apikey": "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3",
        "text": "аптека",
        "lang": "ru_RU",
        "ll": f"{lon},{lat}",
        "type": "biz",
        "results": 1
    }

    response = requests.get(search_api_server, params=search_params)
    if not response.ok:
        raise RuntimeError(f"Ошибка поиска аптек: {response.status_code}")

    json_response = response.json()
    if not json_response.get("features"):
        raise RuntimeError("Аптеки не найдены")

    org = json_response["features"][0]
    org_name = org["properties"]["CompanyMetaData"]["name"]
    org_address = org["properties"]["CompanyMetaData"]["address"]
    org_hours = org["properties"]["CompanyMetaData"].get(
        "Hours", {}).get("text", "Время работы не указано")
    org_pos = org["geometry"]["coordinates"]

    return {
        "name": org_name,
        "address": org_address,
        "hours": org_hours,
        "pos": org_pos
    }


def generate_map(point1, point2):
    center, zoom = calculate_center_and_zoom(point1, point2)

    map_api_server = "http://static-maps.yandex.ru/1.x/"
    map_params = {
        "l": "map",
        "ll": center,
        "z": str(int(zoom)),
        "pt": f"{point1[0]},{point1[1]},pm2rdm~{point2[0]},{point2[1]},pm2gnm"
    }

    response = requests.get(map_api_server, params=map_params)
    if not response.ok:
        raise RuntimeError(f"Ошибка получения карты: {response.status_code}")

    return response.content


def print_snippet(address, pharmacy, distance):
    print("\n" + "="*50)
    print(f"Исходный адрес: {address}")
    print("\nБлижайшая аптека:")
    print(f"Название: {pharmacy['name']}")
    print(f"Адрес: {pharmacy['address']}")
    print(f"Время работы: {pharmacy['hours']}")
    print(f"Расстояние: {distance:.2f} км")
    print("="*50 + "\n")


def main():
    if len(sys.argv) < 2:
        print("Использование: python main.py 'адрес'")
        return

    address = " ".join(sys.argv[1:])

    try:
        toponym, (lon, lat) = geocode_address(address)
        address_text = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]

        pharmacy = find_nearest_pharmacy(lon, lat)
        ph_lon, ph_lat = pharmacy["pos"]

        distance = haversine_distance(
            float(lon), float(lat), float(ph_lon), float(ph_lat))

        map_image = generate_map((lon, lat), (ph_lon, ph_lat))

        with open("map.png", "wb") as f:
            f.write(map_image)

        print_snippet(address_text, pharmacy, distance)
        print("Карта сохранена в файл map.png")

    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()
