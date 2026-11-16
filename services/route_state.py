"""Зберігаємо останній обраний маршрут і на диску, і в пам'яті.

Ніяких змін у stations_list.json та routes_list.json немає.
Після натискання кнопки автоматично створюється data/selected_route.json.
"""
import json
from pathlib import Path

# __file__ — цей файл: services/route_state.py.
# parent.parent — папка проєкту hackathon-cs201.
FILE_PATH = Path(__file__).resolve().parent.parent / "data" / "selected_route.json"


def load_route():
    """Прочитати останній маршрут з диска (можна з іншого процесу)."""
    if not FILE_PATH.exists():
        return {}

    with open(FILE_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


# Один спільний словник для модулів, що працюють в одному процесі.
route = load_route()


def update_route(start, finish, delays, min_transfer, max_transfer):
    """Перевірити п'ять значень і зберегти маршрут у JSON."""
    # Перевіряємо дані також тут: це захист від неправильного виклику
    # update_route() іншим модулем, який не використовує нашу форму.
    if (type(min_transfer) is not int or type(max_transfer) is not int):
        raise ValueError("Час пересадки має бути цілим числом хвилин.")
    if min_transfer < 0 or max_transfer < 0 or min_transfer > max_transfer:
        raise ValueError("Неправильний мінімальний або максимальний час пересадки.")

    new_route = {
        "departure_station": start,
        "arrival_station": finish,
        "consider_delays": bool(delays),
        "min_transfer_minutes": min_transfer,
        "max_transfer_minutes": max_transfer
    }

    # Кожне натискання кнопки перезаписує окремий файл із поточним маршрутом.
    # Існуючі JSON зі станціями та поїздами не змінюються.
    FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(FILE_PATH, "w", encoding="utf-8") as file:
        json.dump(new_route, file, ensure_ascii=False, indent=4)

    # Оновлюємо той самий словник, щоб імпорти
    # `from route_state import route` бачили нові значення в цьому процесі.
    route.clear()
    route.update(new_route)
    return route
