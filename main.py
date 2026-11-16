

from services.loader import DataLoader


def main():
    loader = DataLoader()
    stations, routes = loader.load_all()

    print(stations)

if __name__ == "__main__":
    main()