import math


def time_to_minutes(time):
    if time is None:
        return None

    hours, minutes = map(int, time.split(":"))
    return hours * 60 + minutes


def minutes_to_time(minutes):
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"


def find_station_index(route, station_name):
    for index, station in enumerate(route["stations"]):
        if station["name"] == station_name:
            return index

    return None


def filter_routes(
    routes,
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

    for route in routes:
        start_index = find_station_index(route, start_station)
        end_index = find_station_index(route, end_station)

        if start_index is None or end_index is None:
            continue

        if start_index >= end_index:
            continue

        departure = route["stations"][start_index]["departure_time"]
        arrival = route["stations"][end_index]["arrival_time"]

        if departure is None or arrival is None:
            continue

        results.append({
            "type": "direct",
            "first_train": route["number"],
            "second_train": None,
            "transfer_station": None,
            "departure_time": departure,
            "arrival_time": arrival,
            "transfer_minutes": 0
        })

    for first_route in routes:
        start_index = find_station_index(first_route, start_station)

        if start_index is None:
            continue

        start_departure = first_route["stations"][start_index]["departure_time"]

        if start_departure is None:
            continue

        for transfer_index in range(start_index + 1, len(first_route["stations"])):
            transfer_station = first_route["stations"][transfer_index]

            arrival = transfer_station["arrival_time"]

            if arrival is None:
                continue

            arrival_minutes = time_to_minutes(arrival)

            if consider_delays:
                arrival_minutes += first_route.get("typical_delay_minutes", 0)

            earliest_departure = arrival_minutes + min_transfer_minutes

            for second_route in routes:

                if second_route["number"] == first_route["number"]:
                    continue

                second_transfer_index = find_station_index(
                    second_route,
                    transfer_station["name"]
                )

                end_index = find_station_index(second_route, end_station)

                if second_transfer_index is None or end_index is None:
                    continue

                if second_transfer_index >= end_index:
                    continue

                departure = second_route["stations"][second_transfer_index]["departure_time"]
                final_arrival = second_route["stations"][end_index]["arrival_time"]

                if departure is None or final_arrival is None:
                    continue

                departure_minutes = time_to_minutes(departure)

                days_to_add = max(
                    0,
                    math.ceil((earliest_departure - departure_minutes) / 1440)
                )

                aligned_departure = departure_minutes + days_to_add * 1440

                transfer_time = aligned_departure - arrival_minutes

                if min_transfer_minutes <= transfer_time <= max_transfer_minutes:
                    results.append({
                        "type": "transfer",
                        "first_train": first_route["number"],
                        "second_train": second_route["number"],
                        "transfer_station": transfer_station["name"],
                        "departure_time": start_departure,
                        "arrival_time": final_arrival,
                        "first_train_arrival": arrival,
                        "first_train_arrival_with_delay": minutes_to_time(arrival_minutes),
                        "second_train_departure": departure,
                        "second_train_departure_aligned": minutes_to_time(aligned_departure),
                        "transfer_minutes": transfer_time
                    })

    results.sort(key=lambda item: item["transfer_minutes"])

    return results
