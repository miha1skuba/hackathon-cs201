import json
from pathlib import Path

# Шлях до файлу, де зберігатиметься обраний маршрут.
# Файл буде створено автоматично.
FILE_PATH = Path(__file__).parent.parent / "data" / "selected_route.json"


def load_route():
    """Завантажити раніше збережений маршрут."""

    # Якщо файлу поки немає, повертаємо порожній словник.
    if not FILE_PATH.exists():
        return {}

    with open(FILE_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


# Спільний словник, доступний іншим модулям.
route = load_route()


def update_route(start, finish, delays):
    """Оновити маршрут і зберегти його у файл."""

    # Очищаємо старий маршрут.
    route.clear()

    # Записуємо нові дані.
    route.update({
        "departure_station": start,
        "arrival_station": finish,
        "consider_delays": bool(delays)
    })

    # Зберігаємо словник на диску.
    with open(FILE_PATH, "w", encoding="utf-8") as file:
        json.dump(route, file, ensure_ascii=False, indent=4)

    return route

print(route)