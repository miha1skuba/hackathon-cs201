import json
import pprint
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
from services.stations import STATIONS, find_stations, resolve_station
from services.route_state import update_route
from services.output_frame import OutputWindow  # Друге вікно результатів

NAVY = "#142C73"
BLUE = "#315CC8"
SKY = "#E9F0FF"
PAGE = "#F3F6FC"
WHITE = "#FFFFFF"
INK = "#16284A"
MUTED = "#73829D"
BORDER = "#DCE5F2"

ctk.set_appearance_mode("light")


class StationField(ctk.CTkFrame):
    """Поле станції з підказками. Однакове для «Звідки» та «Куди»."""

    def __init__(self, master, title, hint, on_change):
        super().__init__(master, fg_color="transparent")
        self.on_change = on_change
        self.text = tk.StringVar()  # Текст, який вводить користувач.
        self.matches = []          # До 5 знайдених назв станцій.
        self.selecting = False     # Не показуємо підказки при автоматичному виборі.
        self.highlight_index = -1  # -1 означає, що жодну підказку ще не виділено.
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text=title, text_color=INK,
                     font=ctk.CTkFont(size=15, weight="bold"), anchor="w"
                     ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        self.entry = ctk.CTkEntry(
            self, textvariable=self.text, height=50, corner_radius=12,
            fg_color="#F8FAFE", border_width=1, border_color=BORDER,
            text_color=INK, font=ctk.CTkFont(size=16))
        self.entry.grid(row=1, column=0, sticky="ew")

        ctk.CTkLabel(self, text=hint, text_color=MUTED,
                     font=ctk.CTkFont(size=12), anchor="w"
                     ).grid(row=2, column=0, sticky="w", pady=(6, 0))

        # Рамка з підказками спочатку прихована.
        self.dropdown = ctk.CTkFrame(
            self, fg_color=SKY, corner_radius=12,
            border_width=1, border_color=BORDER)
        self.dropdown.grid(row=3, column=0, sticky="ew", pady=(7, 0))
        self.dropdown.grid_columnconfigure(0, weight=1)
        self.dropdown.grid_remove()

        # Запускаємо пошук після кожної зміни введеного тексту.
        self.text.trace_add("write", self.show_suggestions)
        # Керування підказками з клавіатури:
        # ↑ / ↓         — перейти на попередню / наступну станцію;
        # Page Up/Down  — відразу перейти на першу / останню станцію;
        # Enter         — вибрати виділену станцію;
        # Escape        — приховати список підказок.
        self.entry.bind("<Up>", self.move_up)
        self.entry.bind("<Down>", self.move_down)
        self.entry.bind("<Prior>", self.page_up)  # Prior — назва клавіші Page Up у Tkinter.
        self.entry.bind("<Next>", self.page_down) # Next — назва клавіші Page Down.
        self.entry.bind("<Return>", self.select_first)
        self.entry.bind("<Escape>", self.hide_suggestions)

    def show_suggestions(self, *_):
        """Коли змінюється текст — заново шукаємо відповідні станції."""
        if self.selecting:
            return

        # Цю функцію ми вже маємо в stations.py.
        self.matches = find_stations(self.text.get())
        self.highlight_index = -1  # Новий запит — скидаємо попередній вибір.
        self.draw_suggestions()
        self.on_change()  # Оновлюємо попередній перегляд маршруту.

    def draw_suggestions(self):
        """Показати кнопки станцій та підсвітити вибрану клавіатурою."""
        # Спочатку знищуємо кнопки від попереднього пошуку.
        for widget in self.dropdown.winfo_children():
            widget.destroy()

        if not self.matches:
            self.dropdown.grid_remove()
            return

        # Є результати — робимо список видимим.
        self.dropdown.grid()

        for i, station in enumerate(self.matches):
            # Вибрана стрілками станція має світло-синій фон.
            is_selected = (i == self.highlight_index)

            ctk.CTkButton(
                self.dropdown,
                text="⌖   " + station,
                height=37,
                anchor="w",
                corner_radius=8,
                fg_color="#D5E3FF" if is_selected else "transparent",
                hover_color="#D5E3FF",
                text_color=INK,
                font=ctk.CTkFont(size=14),
                command=lambda name=station: self.choose(name)
            ).grid(row=i, column=0, sticky="ew", padx=5, pady=2)

    def move_down(self, event=None):
        """Стрілка ↓: наступна станція (після останньої — перша)."""
        if self.matches:
            self.highlight_index = (self.highlight_index + 1) % len(self.matches)
            self.draw_suggestions()
        return "break"  # Не даємо Tkinter додатково обробляти натискання.

    def move_up(self, event=None):
        """Стрілка ↑: попередня станція (перед першою — остання)."""
        if self.matches:
            self.highlight_index = (self.highlight_index - 1) % len(self.matches)
            self.draw_suggestions()
        return "break"

    def page_down(self, event=None):
        """Page Down: виділити останню станцію зі списку."""
        if self.matches:
            self.highlight_index = len(self.matches) - 1
            self.draw_suggestions()
        return "break"

    def page_up(self, event=None):
        """Page Up: виділити першу станцію зі списку."""
        if self.matches:
            self.highlight_index = 0
            self.draw_suggestions()
        return "break"

    def choose(self, station):
        """Записати обрану назву в поле та прибрати список підказок."""
        self.selecting = True  # Тимчасово вимикаємо реакцію на зміну тексту.
        self.text.set(station)
        self.selecting = False

        self.matches = []
        self.highlight_index = -1
        self.dropdown.grid_remove()
        self.on_change()
        self.entry.focus_set()  # Можна відразу продовжити вводити текст.

    def get_station(self):
        """Повернути справжню назву зі списку або None, якщо її немає."""
        return resolve_station(self.text.get())

    def select_first(self, event=None):
        """Enter вибирає виділену станцію; якщо нема виділення — першу."""
        if self.matches:
            index = self.highlight_index if self.highlight_index >= 0 else 0
            self.choose(self.matches[index])
        return "break"

    def hide_suggestions(self, event=None):
        """Escape приховує підказки, не очищаючи введену назву."""
        self.dropdown.grid_remove()
        self.matches = []
        self.highlight_index = -1
        return "break"


class TrainRouteApp(ctk.CTk):
    """Основне вікно. Найважливіша змінна — self.route."""

    def __init__(self):
        super().__init__()
        self.title("Rail Route • Пошук маршруту")
        self.geometry("940x820")
        self.minsize(680, 640)
        self.configure(fg_color=PAGE)

        self.route = None  # Обрані параметри маршруту.
        self.output_window = None  # Посилання на друге вікно (створимо пізніше).
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.build_header()
        self.body = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.body.grid(row=1, column=0, sticky="nsew")
        self.body.grid_columnconfigure(0, weight=1)
        self.build_form()
        self.build_footer()

    def build_header(self):
        """Темно-синя верхня панель — як у попередній версії."""
        header = ctk.CTkFrame(self, fg_color=NAVY, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        brand = ctk.CTkFrame(header, fg_color="transparent")
        brand.grid(row=0, column=0, sticky="w", padx=55, pady=(24, 6))
        ctk.CTkLabel(brand, text="УЗ", fg_color=WHITE, text_color=NAVY,
                     width=43, height=34, corner_radius=10,
                     font=ctk.CTkFont(size=18, weight="bold")
                     ).pack(side="left", padx=(0, 12))
        ctk.CTkLabel(brand, text="RAIL ROUTE  /  ПЛАНУВАЛЬНИК ПОЇЗДОК",
                     text_color="#D5E3FF", font=ctk.CTkFont(size=12, weight="bold")
                     ).pack(side="left")
        ctk.CTkLabel(header, text="Куди вирушаємо?", text_color=WHITE,
                     font=ctk.CTkFont(size=31, weight="bold"), anchor="w"
                     ).grid(row=1, column=0, sticky="ew", padx=55, pady=(2, 0))
        ctk.CTkLabel(header, text="Оберіть станції та налаштуйте параметри пошуку",
                     text_color="#CDD9FB", font=ctk.CTkFont(size=14), anchor="w"
                     ).grid(row=2, column=0, sticky="ew", padx=55, pady=(5, 24))

    def build_form(self):
        """Біла картка з полями, галочкою та головною кнопкою."""
        card = ctk.CTkFrame(self.body, fg_color=WHITE, corner_radius=22,
                            border_width=1, border_color=BORDER)
        card.grid(row=0, column=0, sticky="ew", padx=50, pady=(25, 15))
        card.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=30, pady=(24, 18))
        top.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(top, text="Ваш маршрут", text_color=INK,
                     font=ctk.CTkFont(size=20, weight="bold")
                     ).grid(row=0, column=0, sticky="w")
        # ctk.CTkLabel(top, text=f"{len(STATIONS)} станцій у списку",
        #              fg_color=SKY, text_color=BLUE, corner_radius=10,
        #              font=ctk.CTkFont(size=12), width=160, height=30
        #              ).grid(row=0, column=1, sticky="e")

        # Обидва поля беруть дані з одного services/stations.py.
        self.departure = StationField(card, "Звідки", "Введіть назву або її частину",
                                      on_change=self.update_hint)
        self.departure.grid(row=1, column=0, sticky="ew", padx=30)

        swap_area = ctk.CTkFrame(card, fg_color="transparent")
        swap_area.grid(row=2, column=0, sticky="ew", padx=30, pady=7)
        ctk.CTkButton(swap_area, text="⇅   Поміняти місцями", width=182, height=34,
                      fg_color=SKY, hover_color="#D5E3FF", text_color=BLUE,
                      corner_radius=10, font=ctk.CTkFont(size=13, weight="bold"),
                      command=self.swap_stations).pack(side="right")

        self.arrival = StationField(card, "Куди", "Введіть назву або її частину",
                                    on_change=self.update_hint)
        self.arrival.grid(row=3, column=0, sticky="ew", padx=30)

        # Два числові поля. Значення зберігатимуться у хвилинах.
        # Вони потрібні, бо route_state.update_route() приймає 5 аргументів.
        transfer = ctk.CTkFrame(card, fg_color="#F4F7FC", corner_radius=12)
        transfer.grid(row=4, column=0, sticky="ew", padx=30, pady=(20, 0))
        transfer.grid_columnconfigure(0, weight=1)
        transfer.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            transfer, text="Мінімальна пересадка (хв)", text_color=INK,
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=(15, 8), pady=(15, 6))
        ctk.CTkLabel(
            transfer, text="Максимальна пересадка (хв)", text_color=INK,
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=1, sticky="w", padx=(8, 15), pady=(15, 6))

        self.min_transfer_entry = ctk.CTkEntry(
            transfer, height=45, corner_radius=10, fg_color=WHITE,
            border_color=BORDER, text_color=INK
        )
        self.min_transfer_entry.grid(row=1, column=0, sticky="ew", padx=(15, 8), pady=(0, 15))
        self.min_transfer_entry.insert(0, "15")

        self.max_transfer_entry = ctk.CTkEntry(
            transfer, height=45, corner_radius=10, fg_color=WHITE,
            border_color=BORDER, text_color=INK
        )
        self.max_transfer_entry.grid(row=1, column=1, sticky="ew", padx=(8, 15), pady=(0, 15))
        self.max_transfer_entry.insert(0, "180")

        # BooleanVar зберігає True або False для майбутнього self.route.
        self.delay_var = tk.BooleanVar(value=False)

        # Рамка тепер клікабельна ВСЯ, а не лише маленький квадратик.
        option = ctk.CTkFrame(card, fg_color="#F4F7FC", corner_radius=12)
        option.grid(row=5, column=0, sticky="ew", padx=30, pady=(24, 15))
        option.grid_columnconfigure(1, weight=1)

        # Сам чекбокс уже вміє змінювати BooleanVar при натисканні.
        # Тому на чекбокс НЕ додаємо ще один обробник кліку.
        ctk.CTkCheckBox(
            option, text="", width=28, height=28,
            checkbox_width=22, checkbox_height=22,
            fg_color=BLUE, hover_color="#2348A6", border_color=BLUE,
            variable=self.delay_var, onvalue=True, offvalue=False
        ).grid(row=0, column=0, rowspan=2, padx=(17, 8), pady=17)

        title_label = ctk.CTkLabel(
            option, text="Враховувати затримки руху поїздів",
            text_color=INK, font=ctk.CTkFont(size=14, weight="bold"), anchor="w"
        )
        title_label.grid(row=0, column=1, sticky="w", pady=(12, 0))

        detail_label = ctk.CTkLabel(
            option, text="Зберегти цей параметр для майбутньої логіки пошуку",
            text_color=MUTED, font=ctk.CTkFont(size=12), anchor="w"
        )
        detail_label.grid(row=1, column=1, sticky="w", pady=(0, 12))

        # Натискання на фон або будь-який із двох написів міняє галочку.
        # Для дочірніх написів потрібно додати bind окремо:
        # події кліку у Tkinter НЕ переходять автоматично до батьківської рамки.
        option.bind("<Button-1>", self.toggle_delay)
        title_label.bind("<Button-1>", self.toggle_delay)
        detail_label.bind("<Button-1>", self.toggle_delay)

        self.error_label = ctk.CTkLabel(card, text="", text_color="#C7384D",
                                        font=ctk.CTkFont(size=13), anchor="w")
        self.error_label.grid(row=6, column=0, sticky="ew", padx=30)
        ctk.CTkButton(card, text="Знайти маршрут  →", height=54,
                      fg_color=BLUE, hover_color="#2348A6", corner_radius=12,
                      font=ctk.CTkFont(size=16, weight="bold"),
                      command=self.create_route
                      ).grid(row=7, column=0, sticky="ew", padx=30, pady=(10, 27))

    def toggle_delay(self, event=None):
        """Перемкнути галочку при натисканні на будь-яке місце картки."""
        self.delay_var.set(not self.delay_var.get())

    def build_footer(self):
        ctk.CTkLabel(
            self.body,
            text="Демо форми • не офіційний застосунок Укрзалізниці • без API та реальних затримок",
            text_color=MUTED, font=ctk.CTkFont(size=11)
        ).grid(row=2, column=0, pady=(0, 18))

    # ========== ЛОГІКА ПІСЛЯ ВВЕДЕННЯ ==========
    def update_hint(self):
        """Показуємо вибраний напрямок у нижній картці."""
        if not hasattr(self, "route_hint"):
            return
        start = self.departure.get_station()
        finish = self.arrival.get_station()
        self.route_hint.configure(text=f"{start or 'Станція відправлення'}  →  "
                                       f"{finish or 'Станція прибуття'}")

    def swap_stations(self):
        """Міняємо вміст двох полів місцями."""
        start = self.departure.text.get()
        finish = self.arrival.text.get()
        self.departure.choose(finish)
        self.arrival.choose(start)
        self.error_label.configure(text="")

    def create_route(self):
        """Кнопка «Знайти маршрут»: зберігаємо запит і відкриваємо нове вікно."""
        # Крок 1. Беремо станції та перевіряємо, чи вони існують у JSON.
        start = self.departure.get_station()
        finish = self.arrival.get_station()

        if start is None or finish is None:
            self.error_label.configure(text="Оберіть обидві станції зі списку підказок.")
            return
        if start == finish:
            self.error_label.configure(text="Станції відправлення й прибуття мають відрізнятися.")
            return

        # Крок 2. Перевіряємо числа: час пересадки в цілих хвилинах.
        try:
            min_time = int(self.min_transfer_entry.get())
            max_time = int(self.max_transfer_entry.get())
        except ValueError:
            self.error_label.configure(text="Час пересадки має бути цілим числом хвилин.")
            return

        if min_time < 0 or max_time < min_time:
            self.error_label.configure(text="Мінімальний час має бути ≥ 0 і не більшим за максимальний.")
            return

        # Крок 3. route_state.py зберігає усі 5 параметрів у selected_route.json.
        try:
            self.route = update_route(
                start, finish, self.delay_var.get(), min_time, max_time
            )
        except (ValueError, OSError) as error:
            self.error_label.configure(text=f"Не вдалося зберегти маршрут: {error}")
            return

        # Крок 4. Залишаємо старий перегляд словника і кнопки копіювання.
        self.error_label.configure(text="")
        print("Збережений маршрут:", self.route)

        # Крок 5. Відкриваємо друге вікно, не закриваючи головну форму.
        self.open_output_window()

    def open_output_window(self):
        """Відкриваємо output_frame.py з актуальними параметрами маршруту."""
        # Не створюємо кілька застарілих вікон одночасно.
        if self.output_window is not None and self.output_window.winfo_exists():
            self.output_window.destroy()

        # Передаємо копію, щоб дані вікна не змінювалися випадково.
        self.output_window = OutputWindow(self, self.route.copy())

    def set_output(self, text):
        """Оновити нижнє поле з текстом (воно недоступне для редагування)."""
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("1.0", text)
        self.output.configure(state="disabled")

    def copy_route(self):
        if self.route is None:
            return
        self.clipboard_clear()
        self.clipboard_append(pprint.pformat(self.route, sort_dicts=False))
        self.update()

    def save_route(self):
        """За бажанням зберегти НОВИЙ JSON; існуючі файли не чіпаємо."""
        if self.route is None:
            return
        filename = filedialog.asksaveasfilename(
            parent=self, defaultextension=".json", initialfile="route_settings.json",
            filetypes=[("JSON files", "*.json")])
        if not filename:
            return
        try:
            with open(filename, "w", encoding="utf-8") as file:
                json.dump(self.route, file, ensure_ascii=False, indent=4)
        except OSError as error:
            self.error_label.configure(text=f"Помилка збереження: {error}")
        else:
            self.error_label.configure(text="JSON успішно збережено.")


if __name__ == "__main__":
    app = TrainRouteApp()
    app.mainloop()

