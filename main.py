from services.matrix import Matrix
from services.loader import DataLoader


def main():
    loader = DataLoader()
    stations, routes = loader.load_all()

    matrix = Matrix(stations, routes)

if __name__ == "__main__":
    main()