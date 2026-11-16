"""Друге вікно Rail Route: показує готовий список результатів пошуку.

Цей модуль нічого не шукає та не змінює алгоритм команди.
Він тільки отримує:
    route   — параметри форми (словник із 5 значень);
    results — список словників типу direct або transfer.

Приклад виклику з app.py:
    OutputWindow(self, self.route, results)

first_train та second_train можуть бути об'єктами models.route.Route.
Якщо команда поки передає тільки номери поїздів, вони теж відобразяться,
але розгорнутий список зупинок стане доступним лише з об'єктами Route.
"""

import customtkinter as ctk

# Ті самі кольори, що в головній формі.
NAVY = "#142C73"
BLUE = "#315CC8"
SKY = "#E9F0FF"
PAGE = "#F3F6FC"
WHITE = "#FFFFFF"
INK = "#16284A"
MUTED = "#73829D"
BORDER = "#DCE5F2"


def get_value(obj, key, default=None):
    """Отримує поле і зі словника, і зі звичайного Python-об'єкта."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def train_number(train):
    """Повертає № поїзда, а не напис на кшталт '<Route object at ...>'."""
    if train is None:
        return "—"

    # Поточний RouteFilter повертає рядок/число, майбутній — Route.
    if isinstance(train, (str, int)):
        return str(train)

    number = get_value(train, "number")
    if number is None and callable(getattr(train, "get_number", None)):
        number = train.get_number()
    return str(number) if number is not None else "—"


def segment_stops(train, from_station, to_station):
    """Повертає зупинки поїзда ТІЛЬКИ на потрібній частині маршруту.

    У models.route.Route поле stations — словник {назва: Stop}.
    Якщо маємо лише номер поїзда, інформації про зупинки поки немає.
    """
    stations = get_value(train, "stations")
    if stations is None:
        return []

    stops = list(stations.values()) if isinstance(stations, dict) else list(stations)
    names = [get_value(stop, "station_name", get_value(stop, "name")) for stop in stops]

    # Шукаємо індекси станцій відправлення і прибуття в цьому поїзді.
    try:
        start_index = names.index(from_station)
        finish_index = names.index(to_station)
    except ValueError:
        return []

    if start_index > finish_index:
        return []

    return stops[start_index:finish_index + 1]


class OutputWindow(ctk.CTkToplevel):
    """Окреме вікно з карткою на кожен знайдений варіант поїздки."""

    def __init__(self, master, route, results=None):
        super().__init__(master)

        self.route = route or {}
        # None означає «результати ще не передали», [] — «нічого не знайдено».
        self.results = results

        self.title("Rail Route • Результати пошуку")
        self.geometry("940x740")
        self.minsize(660, 550)
        self.configure(fg_color=PAGE)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.build_header()

        # Сторінка прокручується коліщатком миші, якщо карток багато.
        self.body = ctk.CTkScrollableFrame(
            self, fg_color="transparent", corner_radius=0
        )
        self.body.grid(row=1, column=0, sticky="nsew")
        self.body.grid_columnconfigure(0, weight=1)

        self.build_route_card()
        self.build_results()

        self.lift()
        self.focus()

    def build_header(self):
        """Верхня синя панель, така сама за стилем, як в app.py."""
        header = ctk.CTkFrame(self, fg_color=NAVY, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header, text="УЗ   RAIL ROUTE  /  РЕЗУЛЬТАТИ ПОШУКУ",
            text_color="#D5E3FF", font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        ).grid(row=0, column=0, sticky="ew", padx=50, pady=(24, 9))

        ctk.CTkLabel(
            header, text="Варіанти вашої поїздки",
            text_color=WHITE, font=ctk.CTkFont(size=30, weight="bold"),
            anchor="w"
        ).grid(row=1, column=0, sticky="ew", padx=50)

        ctk.CTkLabel(
            header, text="Оберіть зручний прямий рейс або поїздку з пересадкою",
            text_color="#CDD9FB", font=ctk.CTkFont(size=14), anchor="w"
        ).grid(row=2, column=0, sticky="ew", padx=50, pady=(5, 22))

    def build_route_card(self):
        """Відображає п'ять параметрів із головної форми."""
        card = ctk.CTkFrame(
            self.body, fg_color=WHITE, corner_radius=22,
            border_width=1, border_color=BORDER
        )
        card.grid(row=0, column=0, sticky="ew", padx=45, pady=(24, 15))
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card, text="Ваш напрямок", text_color=MUTED,
            font=ctk.CTkFont(size=13), anchor="w"
        ).grid(row=0, column=0, sticky="ew", padx=26, pady=(23, 6))

        start = self.route.get("departure_station", "—")
        finish = self.route.get("arrival_station", "—")

        ctk.CTkLabel(
            card, text=f"{start}   →   {finish}", text_color=INK,
            font=ctk.CTkFont(size=23, weight="bold"),
            anchor="w", wraplength=740, justify="left"
        ).grid(row=1, column=0, sticky="ew", padx=26, pady=(0, 14))

        min_time = self.route.get("min_transfer_minutes", "—")
        max_time = self.route.get("max_transfer_minutes", "—")
        delays = "Так" if self.route.get("consider_delays", False) else "Ні"

        details = ctk.CTkFrame(card, fg_color=SKY, corner_radius=12)
        details.grid(row=2, column=0, sticky="ew", padx=26, pady=(0, 15))
        ctk.CTkLabel(
            details,
            text=f"Пересадка: {min_time}–{max_time} хв    •    Враховувати затримки: {delays}",
            text_color=BLUE, font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w", wraplength=730, justify="left"
        ).pack(fill="x", padx=14, pady=12)

        ctk.CTkButton(
            card, text="←  Змінити параметри", width=195, height=38,
            corner_radius=10, fg_color=SKY, hover_color="#D5E3FF",
            text_color=BLUE, command=self.destroy
        ).grid(row=3, column=0, sticky="w", padx=26, pady=(0, 23))

    def build_results(self):
        """Створює стільки карток, скільки словників прийшло у results."""
        section = ctk.CTkFrame(
            self.body, fg_color=WHITE, corner_radius=22,
            border_width=1, border_color=BORDER
        )
        section.grid(row=1, column=0, sticky="ew", padx=45, pady=(0, 24))
        section.grid_columnconfigure(0, weight=1)
        self.results_area = section  # Місце, куди малюються картки.

        count = len(self.results) if isinstance(self.results, list) else 0
        title = f"Доступні маршрути ({count})" if self.results is not None else "Доступні маршрути"
        ctk.CTkLabel(
            section, text=title, text_color=INK,
            font=ctk.CTkFont(size=20, weight="bold"), anchor="w"
        ).grid(row=0, column=0, sticky="ew", padx=26, pady=(23, 6))

        # Поки результатів немає — не вигадуємо поїзди.
        if not self.results:
            message = (
                "Очікуємо результати від алгоритму пошуку."
                if self.results is None
                else "За обраними параметрами маршрути не знайдено."
            )
            ctk.CTkLabel(
                section, text=message, text_color=MUTED,
                font=ctk.CTkFont(size=14), wraplength=600
            ).grid(row=1, column=0, padx=26, pady=(30, 44))
            return

        # Один словник -> одна окрема картка. Порядок результатів зберігаємо.
        for index, result in enumerate(self.results, start=1):
            self.build_result_card(section, result, index)

    def build_result_card(self, parent, result, index):
        """Малює прямий рейс або маршрут із двома поїздами."""
        card = ctk.CTkFrame(
            parent, fg_color="#F8FAFE", corner_radius=15,
            border_width=1, border_color=BORDER
        )
        card.grid(row=index, column=0, sticky="ew", padx=26, pady=(10, 14))
        card.grid_columnconfigure(0, weight=1)

        is_transfer = result.get("type") == "transfer"
        kind = "З пересадкою" if is_transfer else "Прямий рейс"

        heading = ctk.CTkFrame(card, fg_color="transparent")
        heading.grid(row=0, column=0, sticky="ew", padx=19, pady=(17, 10))
        heading.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            heading, text=f"Варіант {index}", text_color=INK,
            font=ctk.CTkFont(size=17, weight="bold")
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            heading, text=kind, fg_color=SKY, corner_radius=9,
            text_color=BLUE, font=ctk.CTkFont(size=13, weight="bold"),
            width=130, height=30
        ).grid(row=0, column=1, sticky="e")

        departure = result.get("departure_time") or "—"
        arrival = result.get("arrival_time") or "—"
        ctk.CTkLabel(
            card, text=f"{departure}     →     {arrival}",
            text_color=NAVY, font=ctk.CTkFont(size=25, weight="bold"),
            anchor="w"
        ).grid(row=1, column=0, sticky="ew", padx=19)
        ctk.CTkLabel(
            card,
            text=f"{self.route.get('departure_station', '—')}  →  {self.route.get('arrival_station', '—')}",
            text_color=MUTED, font=ctk.CTkFont(size=13), anchor="w",
            wraplength=680, justify="left"
        ).grid(row=2, column=0, sticky="ew", padx=19, pady=(3, 14))

        start = self.route.get("departure_station", "—")
        finish = self.route.get("arrival_station", "—")

        if is_transfer:
            transfer = result.get("transfer_station") or "—"
            self.build_train_leg(
                card, 3, result.get("first_train"), start, transfer,
                departure, result.get("first_train_arrival"),
                "Перший поїзд"
            )
            self.build_transfer_details(card, result, 4)
            self.build_train_leg(
                card, 5, result.get("second_train"), transfer, finish,
                result.get("second_train_departure_aligned")
                or result.get("second_train_departure"), arrival,
                "Другий поїзд"
            )
            bottom_row = 6
        else:
            self.build_train_leg(
                card, 3, result.get("first_train"), start, finish,
                departure, arrival, "Поїзд"
            )
            bottom_row = 4

        # Нижній порожній відступ у кожній картці.
        ctk.CTkFrame(card, fg_color="transparent", height=9).grid(
            row=bottom_row, column=0
        )

    def build_train_leg(self, parent, row, train, origin, destination,
                        departure, arrival, label):
        """Один поїзд: №, ділянка, часи та кнопка для перегляду зупинок."""
        leg = ctk.CTkFrame(parent, fg_color=WHITE, corner_radius=12)
        leg.grid(row=row, column=0, sticky="ew", padx=18, pady=(0, 11))
        leg.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            leg, text=f"{label}  •  № {train_number(train)}",
            text_color=BLUE, font=ctk.CTkFont(size=15, weight="bold"), anchor="w"
        ).grid(row=0, column=0, sticky="ew", padx=16, pady=(13, 3))

        ctk.CTkLabel(
            leg, text=f"{origin}  →  {destination}",
            text_color=INK, font=ctk.CTkFont(size=14),
            anchor="w", wraplength=640, justify="left"
        ).grid(row=1, column=0, sticky="ew", padx=16)

        ctk.CTkLabel(
            leg, text=f"Відправлення: {departure or '—'}     Прибуття: {arrival or '—'}",
            text_color=MUTED, font=ctk.CTkFont(size=13), anchor="w",
            wraplength=640, justify="left"
        ).grid(row=2, column=0, sticky="ew", padx=16, pady=(4, 12))

        stops = segment_stops(train, origin, destination)
        if not stops:
            # Коли передано тільки №, ми не можемо вивести зупинки достовірно.
            return

        # Панель зі зупинками спочатку прихована.
        stops_frame = ctk.CTkFrame(leg, fg_color=SKY, corner_radius=10)
        stops_frame.grid(row=4, column=0, sticky="ew", padx=16, pady=(0, 12))
        stops_frame.grid_columnconfigure(0, weight=1)

        for i, stop in enumerate(stops):
            name = get_value(stop, "station_name", get_value(stop, "name", "—"))
            arr_time = get_value(stop, "arrival_time") or "—"
            dep_time = get_value(stop, "departure_time") or "—"

            line = ctk.CTkFrame(stops_frame, fg_color="transparent")
            line.grid(row=i, column=0, sticky="ew", padx=12, pady=4)
            line.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(
                line, text=f"•  {name}", text_color=INK,
                font=ctk.CTkFont(size=13), anchor="w"
            ).grid(row=0, column=0, sticky="w")
            ctk.CTkLabel(
                line, text=f"Приб. {arr_time}  |  Відпр. {dep_time}",
                text_color=MUTED, font=ctk.CTkFont(size=12)
            ).grid(row=0, column=1, sticky="e", padx=(10, 0))

        button = ctk.CTkButton(
            leg, text="▾  Показати зупинки", width=175, height=32,
            fg_color=SKY, hover_color="#D5E3FF", text_color=BLUE,
            corner_radius=9, font=ctk.CTkFont(size=12, weight="bold")
        )
        button.grid(row=3, column=0, sticky="w", padx=16, pady=(0, 11))
        stops_frame.grid_remove()
        button.configure(
            command=lambda: self.toggle_stops(stops_frame, button)
        )

    def toggle_stops(self, frame, button):
        """Розгортає або згортає зупинки одного конкретного поїзда."""
        if frame.winfo_ismapped():
            frame.grid_remove()
            button.configure(text="▾  Показати зупинки")
        else:
            frame.grid()
            button.configure(text="▴  Приховати зупинки")

    def build_transfer_details(self, parent, result, row):
        """Виводить інформацію про пересадку між першим і другим поїздом."""
        transfer = result.get("transfer_station") or "—"
        minutes = result.get("transfer_minutes")
        wait = f"{minutes} хв" if minutes is not None else "—"

        box = ctk.CTkFrame(parent, fg_color=SKY, corner_radius=12)
        box.grid(row=row, column=0, sticky="ew", padx=18, pady=(0, 11))
        box.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            box, text=f"⇄  Пересадка: {transfer}  •  Очікування: {wait}",
            text_color=BLUE, font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w", wraplength=660, justify="left"
        ).grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 5))

        # Час без затримки, скоригований час та відправлення другого поїзда.
        planned = result.get("first_train_arrival") or "—"
        delayed = result.get("first_train_arrival_with_delay") or "—"
        next_departure = (
            result.get("second_train_departure_aligned")
            or result.get("second_train_departure") or "—"
        )
        ctk.CTkLabel(
            box,
            text=(f"Прибуття першого: {planned}  •  З урахуванням затримки: {delayed}\n"
                  f"Відправлення другого: {next_departure}"),
            text_color=INK, font=ctk.CTkFont(size=12),
            anchor="w", justify="left", wraplength=660
        ).grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 13))
