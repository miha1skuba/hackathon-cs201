from pathlib import Path
import json

from models.route import Route
from models.stop import Stop

class DataLoader:
    def __init__(
            self,
            data_path = Path(__file__).parent.parent / "data",
            stations_file = "stations_list.json",
            routes_file = "routes_list.json"
            ):
        self.data_path = data_path
        self.stations_file = stations_file
        self.routes_file = routes_file

    def load_data(self, filename):
        file_path = self.data_path / filename
        with open(file_path, "r") as f:
            data = json.load(f)
        return data

    def load_stations(self):
        return self.load_data(self.stations_file)

    def load_routes(self):
        data = self.load_data(self.routes_file)

        routes = {}

        for route in data:
            stops = {}

            for stop in route["stations"]:
                stops[stop["name"]] = Stop(
                    stop["name"],
                    stop["arrival_time"],
                    stop["departure_time"]
                )

            routes[route["number"]] = Route(
                route["number"],
                route["paired_with"],
                route["type"],
                stops
            )

        return routes
            

    def load_all(self):
        stations = self.load_stations()
        routes = self.load_routes()
        return stations, routes