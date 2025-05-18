import requests
import folium
from config import YANDEX_MAPS_API_KEY


class PharmacyMapGenerator:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://search-maps.yandex.ru/v1/"

    def get_pharmacies_nearby(self, address, count=10):
        geocode_url = f"https://geocode-maps.yandex.ru/1.x/"
        params = {
            "apikey": self.api_key,
            "geocode": address,
            "format": "json"
        }
        response = requests.get(geocode_url, params=params)
        coords = response.json()[
            "response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
        longitude, latitude = coords.split(" ")

        search_params = {
            "apikey": self.api_key,
            "text": "аптека",
            "lang": "ru_RU",
            "ll": f"{longitude},{latitude}",
            "type": "biz",
            "results": count
        }
        response = requests.get(self.base_url, params=search_params)
        return response.json()["features"]

    def generate_map(self, address, output_file="pharmacy_map.html"):
        pharmacies = self.get_pharmacies_nearby(address)

        center_lat = float(pharmacies[0]["geometry"]["coordinates"][1])
        center_lon = float(pharmacies[0]["geometry"]["coordinates"][0])

        m = folium.Map(location=[center_lat, center_lon], zoom_start=14)

        for pharmacy in pharmacies:
            lat = float(pharmacy["geometry"]["coordinates"][1])
            lon = float(pharmacy["geometry"]["coordinates"][0])
            name = pharmacy["properties"]["CompanyMetaData"]["name"]
            hours = pharmacy["properties"]["CompanyMetaData"].get("Hours", {})

            if not hours:
                color = "gray"
                popup_text = f"{name}<br>Время работы: нет данных"
            elif hours.get("Availabilities", {}).get("Everyday", False):
                color = "green"
                popup_text = f"{name}<br>Круглосуточно"
            else:
                color = "blue"
                popup_text = f"{name}<br>Время работы: {hours.get('text', 'не указано')}"

            folium.CircleMarker(
                location=[lat, lon],
                radius=8,
                popup=popup_text,
                color=color,
                fill=True,
                fill_color=color
            ).add_to(m)

        m.save(output_file)
        return output_file
