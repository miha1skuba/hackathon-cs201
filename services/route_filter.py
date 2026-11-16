
import math


class RouteFilter:
    def __init__(self, routes):
        self.routes = list(routes.values()) if isinstance(routes, dict) else routes

    @staticmethod
    def get_value(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    @staticmethod
    def time_to_minutes(time):
        if time is None:
            return None

        hours, minutes = map(int, time.split(":"))
        return hours * 60 + minutes

    @staticmethod
    def minutes_to_time(minutes):
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}"

    def get_stations(self, route):
        stations = self.get_value(route, "stations", {})

        if isinstance(stations, dict):
            return list(stations.values())

        return stations

    def get_station_name(self, station):
        return self.get_value(station, "name",
               self.get_value(station, "station_name"))

    def get_arrival_time(self, station):
        return self.get_value(station, "arrival_time")

    def get_departure_time(self, station):
        return self.get_value(station, "departure_time")

    def get_route_number(self, route):
        return self.get_value(route, "number")

    def get_delay(self, route):
        return self.get_value(route, "typical_delay_minutes", 0)

    def find_station_index(self, route, station_name):
        stations = self.get_stations(route)

        for index, station in enumerate(stations):
            if self.get_station_name(station) == station_name:
                return index

        return None

    def filter_routes(
        self,
        start_station,
        end_station,
        min_transfer_minutes=30,
        max_transfer_minutes=360,
        consider_delays=False
    ):
        if min_transfer_minutes < 0:
            raise ValueError("Мінімальний час пересадки не може бути від'ємним")

        if max_transfer_minutes < min_transfer_minutes:
            raise ValueError("Максимальний час має бути більшим за мінімальний")

        results = []

        for route in self.routes:
            stations = self.get_stations(route)

            start_index = self.find_station_index(route, start_station)
            end_index = self.find_station_index(route, end_station)

            if start_index is None or end_index is None:
                continue

            if start_index >= end_index:
                continue

            departure = self.get_departure_time(stations[start_index])
            arrival = self.get_arrival_time(stations[end_index])

            if departure is None or arrival is None:
                continue

            results.append({
                "type": "direct",
                "first_train": self.get_route_number(route),
                "second_train": None,
                "transfer_station": None,
                "departure_time": departure,
                "arrival_time": arrival,
                "transfer_minutes": 0
            })

        for first_route in self.routes:
            first_stations = self.get_stations(first_route)

            start_index = self.find_station_index(
                first_route, start_station
            )

            if start_index is None:
                continue

            start_departure = self.get_departure_time(
                first_stations[start_index]
            )

            if start_departure is None:
                continue

            for transfer_index in range(
                start_index + 1, len(first_stations)
            ):
                transfer_station = first_stations[transfer_index]
                arrival = self.get_arrival_time(transfer_station)

                if arrival is None:
                    continue

                arrival_minutes = self.time_to_minutes(arrival)

                if consider_delays:
                    arrival_minutes += self.get_delay(first_route)

                earliest_departure = (
                    arrival_minutes + min_transfer_minutes
                )

                for second_route in self.routes:
                    if (
                        self.get_route_number(second_route)
                        == self.get_route_number(first_route)
                    ):
                        continue

                    second_stations = self.get_stations(second_route)

                    second_transfer_index = self.find_station_index(
                        second_route,
                        self.get_station_name(transfer_station)
                    )

                    end_index = self.find_station_index(
                        second_route, end_station
                    )

                    if second_transfer_index is None or end_index is None:
                        continue

                    if second_transfer_index >= end_index:
                        continue

                    departure = self.get_departure_time(
                        second_stations[second_transfer_index]
                    )

                    final_arrival = self.get_arrival_time(
                        second_stations[end_index]
                    )

                    if departure is None or final_arrival is None:
                        continue

                    departure_minutes = self.time_to_minutes(departure)

                    days_to_add = max(
                        0,
                        math.ceil(
                            (earliest_departure - departure_minutes) / 1440
                        )
                    )

                    aligned_departure = (
                        departure_minutes + days_to_add * 1440
                    )

                    transfer_time = aligned_departure - arrival_minutes

                    if (
                        min_transfer_minutes
                        <= transfer_time
                        <= max_transfer_minutes
                    ):
                        aligned_arrival = (
                            self.time_to_minutes(final_arrival)
                            + days_to_add * 1440
                        )

                        results.append({
                            "type": "transfer",
                            "first_train": self.get_route_number(first_route),
                            "second_train": self.get_route_number(second_route),
                            "transfer_station": self.get_station_name(
                                transfer_station
                            ),
                            "departure_time": start_departure,
                            "arrival_time": self.minutes_to_time(
                                aligned_arrival
                            ),
                            "first_train_arrival": arrival,
                            "first_train_arrival_with_delay": (
                                self.minutes_to_time(arrival_minutes)
                            ),
                            "second_train_departure": departure,
                            "second_train_departure_aligned": (
                                self.minutes_to_time(aligned_departure)
                            ),
                            "transfer_minutes": transfer_time
                        })

        results.sort(key=lambda item: item["transfer_minutes"])

        return results

