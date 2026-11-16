import json
from pathlib import Path

file_path = Path(__file__).parent.parent / "data" / "stations_list.json"

with open(file_path, "r", encoding="utf-8") as file:
    STATIONS = json.load(file)


def find_stations(query):
    query = query.strip().casefold()

    if len(query) < 2:
        return []

    return [station for station in STATIONS if query in station.casefold()][:5]


def resolve_station(text):
    text = text.strip().casefold()

    for station in STATIONS:
        if station.casefold() == text:
            return station

    return None