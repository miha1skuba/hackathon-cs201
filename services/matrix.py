class Matrix():
    def __init__(self, stations, routes):
        self.n = len(stations)
        matrix = [[[] for j in range(self.n)] for i in range(self.n)]
        for route in routes.values():
            stops = list(route.stations.values())
            for i in range(len(stops) - 1):
                station_i = stops[i].station_name
                station_j = stops[i + 1].station_name
                matrix[stations.index(station_i)][stations.index(station_j)].append(route.number)
        self.matrix = matrix

    def get_matrix(self):
        return self.matrix
    def get_routes_numbers(self, station_i, station_j):
        return self.matrix[station_i][station_j]
    def search():
        pass