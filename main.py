from services.matrix import Matrix
from services.loader import DataLoader
from services.app import TrainRouteApp


def main():
    loader = DataLoader()
    stations, routes = loader.load_all()

    matrix = Matrix(stations, routes)
    
    app = TrainRouteApp(
 
    )

    # Запускаємо застосунок
    app.mainloop()



if __name__ == "__main__":
    main()