from services.matrix import Matrix
from services.loader import DataLoader
from services.app import TrainRouteApp


def main():
    loader = DataLoader()
    stations, routes = loader.load_all()

    matrix = Matrix(stations, routes)

    app = TrainRouteApp(
        matrix=matrix,
        routes=routes
    )

    app.mainloop()



if __name__ == "__main__":
    main()