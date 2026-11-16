class Route:
    def __init__(self,number,paired_with, type, stations):
        self.number = number
        self.paired_with = paired_with
        self.type = type
        self.stations = stations

    def get_number(self):
        return self.number
    def get_paired_with(self):
        return self.paired_with
    def get_type(self):
        return self.type
    def get_stations(self):
        return self.stations

    def get_station_name(self, station_name):
        for stop in self.stations:
            if stop.get_station_name() == station_name:
                return stop
        return None

    def get_arrival_time(self,station_name):
        stop = self.get_station_name(station_name)
        if stop:
            return stop.get_arrival_time()
        return None

    def get_departure_time(self,station_name):
        stop = self.get_station_name(station_name)
        if stop:
            return stop.get_departure_time()
        return None