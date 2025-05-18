from map_generator import PharmacyMapGenerator


def main():
    generator = PharmacyMapGenerator(YANDEX_MAPS_API_KEY)

    address = input("Введите адрес для поиска аптек рядом: ")

    output_file = generator.generate_map(address)
    print(f"Карта сохранена в файл: {output_file}")


if __name__ == "__main__":
    main()
