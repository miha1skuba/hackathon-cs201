class Stop:
    def __init__(self, station_name, arrival_time, departure_time):
        self.station_name = station_name
        self.arrival_time = arrival_time
        self.departure_time = departure_time
        self.route_number = route_number

    def get_station_name(self):
        return self.station_name
    def get_arrival_time(self):
        return self.arrival_time
    def get_departure_time(self):
        return self.departure_time