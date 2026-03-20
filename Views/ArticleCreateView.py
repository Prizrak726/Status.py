from tkinter import Toplevel, StringVar, Text, END
from tkinter import ttk, messagebox

from Controllers import ArticleController
from Models.Users import Users
from Models.Ticket import Ticket


class ArticleCreateView(Toplevel):
    """
    Окно создания статьи базы знаний из заявки.
    """

    def __init__(self, master, ticket: Ticket, executor: Users) -> None:
        super().__init__(master)
        self.title("Создание статьи")
        self.geometry("600x400")
        self.resizable(width=False, height=False)

        self.ticket = ticket
        self.executor = executor

        self.title_var = StringVar()

        self._build_ui()

    def _build_ui(self) -> None:
        padding = {"padx": 10, "pady": 5}

        ttk.Label(self, text="Название:").grid(row=0, column=0, sticky="w", **padding)
        title_entry = ttk.Entry(self, textvariable=self.title_var, width=50)
        title_entry.grid(row=0, column=1, sticky="ew", **padding)

        ttk.Label(self, text="Описание:").grid(row=1, column=0, sticky="nw", **padding)
        self.description_text = Text(self, height=10, width=50)
        self.description_text.grid(row=1, column=1, sticky="nsew", **padding)

        btn_create = ttk.Button(self, text="Создать", command=self.on_create)
        btn_create.grid(row=2, column=0, sticky="ew", padx=10, pady=(15, 10))

        btn_back = ttk.Button(self, text="Назад", command=self.destroy)
        btn_back.grid(row=2, column=1, sticky="ew", padx=10, pady=(15, 10))

        # по умолчанию в заголовок подставим название заявки
        self.title_var.set(self.ticket.title)
        title_entry.focus_set()

    def on_create(self) -> None:
        title = self.title_var.get().strip()
        description = self.description_text.get("1.0", END).strip()

        if not title or not description:
            messagebox.showwarning("Создание статьи", "Заполните все поля")
            return

        ok, result = ArticleController.create_article(
            title=title,
            description=description,
            ticket_id=self.ticket.id,
            executor_id=self.executor.id,
        )
        if not ok:
            messagebox.showerror("Создание статьи", str(result))
            return

        messagebox.showinfo("Создание статьи", "Статья успешно создана")
        self.destroy()


__all__ = ["ArticleCreateView"]

