"""Друге вікно Rail Route — МАКЕТ майбутньої сторінки результатів.

Поки не шукає поїзди й не використовує routes_list.json.
Коли команда підготує алгоритм, тут можна буде додати картки поїздів.

Як відкрити вікно з app.py:
    OutputWindow(self, self.route)

master — посилання на головне вікно (app.py).
route  — словник із п'ятьма параметрами, які ввів користувач.
"""
import customtkinter as ctk


# Та сама палітра, що й у головній формі app.py.
NAVY = "#142C73"
BLUE = "#315CC8"
SKY = "#E9F0FF"
PAGE = "#F3F6FC"
WHITE = "#FFFFFF"
INK = "#16284A"
MUTED = "#73829D"
BORDER = "#DCE5F2"


class OutputWindow(ctk.CTkToplevel):
    """Окреме вікно, яке показує обраний маршрут і місце для результатів."""

    def __init__(self, master, route):
        super().__init__(master)

        # Зберігаємо отриманий маршрут у цьому вікні.
        # Це ті самі значення, які app.py зберіг у selected_route.json.
        self.route = route

        self.title("Rail Route • Результати пошуку")
        self.geometry("940x740")
        self.minsize(660, 550)
        self.configure(fg_color=PAGE)

        # Робимо одну колонку на всю ширину вікна.
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Будуємо екран трьома невеликими функціями.
        self.build_header()

        self.body = ctk.CTkScrollableFrame(
            self, fg_color="transparent", corner_radius=0
        )
        self.body.grid(row=1, column=0, sticky="nsew")
        self.body.grid_columnconfigure(0, weight=1)

        self.build_route_card()
        self.build_results_placeholder()

        # Виводимо друге вікно поверх головного.
        self.lift()
        self.focus()

    def build_header(self):
        """Темно-синя верхня панель у стилі головної форми."""
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
            header, text="Тут згодом з'являться знайдені поїзди та пересадки",
            text_color="#CDD9FB", font=ctk.CTkFont(size=14), anchor="w"
        ).grid(row=2, column=0, sticky="ew", padx=50, pady=(5, 22))

    def build_route_card(self):
        """Картка з параметрами, які користувач обрав у головній формі."""
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

        start = self.route["departure_station"]
        finish = self.route["arrival_station"]

        ctk.CTkLabel(
            card, text=f"{start}   →   {finish}", text_color=INK,
            font=ctk.CTkFont(size=23, weight="bold"),
            anchor="w", wraplength=740, justify="left"
        ).grid(row=1, column=0, sticky="ew", padx=26, pady=(0, 14))

        min_time = self.route["min_transfer_minutes"]
        max_time = self.route["max_transfer_minutes"]
        delays = "Так" if self.route["consider_delays"] else "Ні"

        # Інформаційний рядок: не кнопки, а відображення обраних параметрів.
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

    def build_results_placeholder(self):
        """Поки ПОРОЖНІЙ блок для результатів. Жодних вигаданих поїздів."""
        card = ctk.CTkFrame(
            self.body, fg_color=WHITE, corner_radius=22,
            border_width=1, border_color=BORDER
        )
        card.grid(row=1, column=0, sticky="ew", padx=45, pady=(0, 24))
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card, text="Доступні маршрути", text_color=INK,
            font=ctk.CTkFont(size=20, weight="bold"), anchor="w"
        ).grid(row=0, column=0, sticky="ew", padx=26, pady=(23, 0))

        # Зберігаємо окрему рамку як self.results_area.
        # Пізніше саме ТУТ можна буде створювати картки для поїздів.
        self.results_area = ctk.CTkFrame(
            card, fg_color="#F5F8FD", corner_radius=14,
            border_width=1, border_color=BORDER
        )
        self.results_area.grid(row=1, column=0, sticky="ew", padx=26, pady=(18, 24))
        self.results_area.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.results_area, text="🚆", font=ctk.CTkFont(size=35)
        ).grid(row=0, column=0, pady=(35, 8))

        ctk.CTkLabel(
            self.results_area, text="Місце для результатів пошуку",
            text_color=INK, font=ctk.CTkFont(size=17, weight="bold")
        ).grid(row=1, column=0, padx=12)

        ctk.CTkLabel(
            self.results_area,
            text="Коли ти передаси формат відповіді алгоритму,\n"
                 "тут з'являться реальні варіанти поїздів і пересадок.",
            text_color=MUTED, font=ctk.CTkFont(size=13), justify="center"
        ).grid(row=2, column=0, pady=(7, 36), padx=12)
