import os
from tkinter import Toplevel, StringVar, Text, END, filedialog
from tkinter import ttk, messagebox

from Controllers import TicketController, ReferenceController
from Models.Users import Users


class CreateTicketView(Toplevel):
    """
    Окно «Создание заявки» с возможностью прикрепления файла.
    """

    def __init__(self, master, current_user: Users, on_created=None) -> None:
        super().__init__(master)
        self.title("Создание заявки")
        self.geometry("1000x450")
        self.resizable(width=False, height=False)

        self.current_user = current_user
        self.on_created = on_created
        self.attachment_path = None

        self.title_var = StringVar()
        self.urgency_var = StringVar()

        self._categories = []
        self._category_map: dict[str, int] = {}

        self._load_categories()
        self._build_ui()

    def _load_categories(self) -> None:
        try:
            self._categories = list(ReferenceController.get_categories())
            self._category_map = {cat.title: int(cat.id) for cat in self._categories}
        except Exception:
            self._categories = []
            self._category_map = {}

    def _build_ui(self) -> None:
        padding = {"padx": 10, "pady": 5}

        ttk.Label(self, text="Название:").grid(row=0, column=0, sticky="w", **padding)
        title_entry = ttk.Entry(self, textvariable=self.title_var, width=50)
        title_entry.grid(row=1, column=0, sticky="ew", **padding)

        ttk.Label(self, text="Категория:").grid(row=0, column=1, sticky="w", **padding)
        self.category_var = StringVar()
        category_combo = ttk.Combobox(
            self,
            textvariable=self.category_var,
            values=list(self._category_map.keys()),
            state="readonly",
            width=48,
        )
        category_combo.grid(row=1, column=1, sticky="ew", **padding)
        if self._category_map:
            category_combo.current(0)

        ttk.Label(self, text="Срочность:").grid(row=0, column=2, sticky="w", **padding)
        urgency_combo = ttk.Combobox(
            self,
            textvariable=self.urgency_var,
            values=["Низкая", "Обычная", "Высокая", "Критичная"],
            state="readonly",
            width=48,
        )
        urgency_combo.grid(row=1, column=2, sticky="ew", **padding)
        urgency_combo.current(1)

        ttk.Label(self, text="Описание:").grid(row=2, column=0, columnspan=3, sticky="nw", **padding)
        self.description_text = Text(self, height=8, width=50)
        self.description_text.grid(row=3, column=0, columnspan=3, sticky="nsew", **padding)

        # Кнопка прикрепления файла
        btn_file = ttk.Button(self, text="Прикрепить файл", command=self.choose_file)
        btn_file.grid(row=4, column=0, sticky="w", padx=10, pady=5)
        self.lbl_file = ttk.Label(self, text="Файл не выбран")
        self.lbl_file.grid(row=4, column=1, columnspan=2, sticky="w", padx=10, pady=5)

        btn_back = ttk.Button(self, text="Назад", command=self.destroy)
        btn_back.grid(row=5, column=0, sticky="ew", padx=10, pady=(15, 10))

        btn_create = ttk.Button(self, text="Создать", command=self.on_create)
        btn_create.grid(row=5, column=2, sticky="ew", padx=10, pady=(15, 10))

        title_entry.focus_set()

    def choose_file(self) -> None:
        filename = filedialog.askopenfilename()
        if filename:
            self.attachment_path = filename
            self.lbl_file.config(text=os.path.basename(filename))

    def on_create(self) -> None:
        title = self.title_var.get().strip()
        description = self.description_text.get("1.0", END).strip()
        category_title = self.category_var.get().strip()
        urgency = self.urgency_var.get().strip()

        if not title or not description or not category_title:
            messagebox.showwarning("Создание заявки", "Заполните все поля")
            return

        category_id = self._category_map.get(category_title)
        if category_id is None:
            messagebox.showerror("Создание заявки", "Категория не выбрана или не найдена")
            return

        # Встраиваем срочность в заголовок и описание
        if urgency:
            full_title = f"[{urgency}] {title}"
            full_description = f"Срочность: {urgency}\n\n{description}"
        else:
            full_title = title
            full_description = description

        ok, result = TicketController.create_ticket(
            title=full_title,
            description=full_description,
            category_id=category_id,
            user_id=self.current_user.id,
            attachment_path=self.attachment_path,
        )
        if not ok:
            messagebox.showerror("Создание заявки", str(result))
            return

        messagebox.showinfo("Создание заявки", "Заявка успешно создана")
        if callable(self.on_created):
            self.on_created()
        self.destroy()


__all__ = ["CreateTicketView"]
