
class Matrix():
    def __init__(self, stations, routes):
        self.n = len(stations)
        matrix = [[[] for j in range(self.n)] for i in range(self.n)]
        self.stations = stations
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



    def find_direct(self, start, end):
        return self.matrix[start][end]

    def find_with_transfer(self, start, end):
        result = []
        for x in range(self.n):
            if x == start or x == end:
                continue
            for train1 in self.matrix[start][x]:
                for train2 in self.matrix[x][end]:
                    if train2 in self.matrix[start][x]:   # зайва пересадка
                        continue
                    result.append((x, train1, train2))
        return result

    def search(self, origin_station: str, destination_station: str):
        if origin_station not in self.stations or destination_station not in self.stations:
            return []

        start = self.stations.index(origin_station)
        end = self.stations.index(destination_station)
        routes = []

        for train in self.find_direct(start, end):
            routes.append([(origin_station, destination_station, train)])

        for x, train1, train2 in self.find_with_transfer(start, end):
            routes.append([
                (origin_station, self.stations[x], train1),
                (self.stations[x], destination_station, train2),
            ])

        return routes

