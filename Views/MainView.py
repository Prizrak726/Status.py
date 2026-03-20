from tkinter import Toplevel, END
from tkinter import ttk, messagebox
from tkinter import StringVar
from Controllers import TicketController
from Models.Role import Role
from Models.Status import Status
from Models.Users import Users

from Views.CreateTicketView import CreateTicketView
from Views.TicketDetailView import TicketDetailView
from Views.KbaseView import KnowledgeBaseView
from Views.UsersView import UsersView
from Views.StatsView import StatsView


class MainView(Toplevel):
    """
    Главное окно «Заявки».
    Список заявок + переходы к другим экранам + фильтрация.
    """

    def __init__(self, master, current_user: Users) -> None:
        super().__init__(master)
        self.title("Заявки")
        self.geometry("1000x600")
        self.resizable(width=True, height=True)

        self.current_user = current_user

        role_obj = getattr(current_user, "role", None)
        role_name = getattr(role_obj, "name", "") if role_obj is not None else ""
        role_id = int(getattr(current_user, "role_id", 0) or 0)

        self.is_admin = role_name == "Администратор" or role_id == Role.ADMIN
        self.is_specialist = role_name == "Специалист" or role_id == Role.SPECIALIST
        self.is_user = role_name == "Пользователь" or role_id == Role.USER

        self._build_ui()
        self.load_tickets()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        # Верхняя панель с кнопками
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", padx=10, pady=5)

        btn_create = ttk.Button(top_frame, text="Создать заявку", command=self.on_create_ticket)
        btn_create.pack(side="left", padx=5)

        btn_kb = ttk.Button(top_frame, text="База знаний", command=self.on_open_kb)
        btn_kb.pack(side="left", padx=5)

        if self.is_admin:
            btn_stats = ttk.Button(top_frame, text="Статистика", command=self.on_open_stats)
            btn_stats.pack(side="left", padx=5)

            btn_users = ttk.Button(top_frame, text="Пользователи", command=self.on_open_users)
            btn_users.pack(side="left", padx=5)

        btn_exit = ttk.Button(top_frame, text="Выход", command=self._on_close)
        btn_exit.pack(side="right", padx=5)

        # Панель фильтров (для специалиста и администратора)
        if not self.is_user:   # специалист или админ
            filter_frame = ttk.LabelFrame(self, text="Фильтры")
            filter_frame.pack(fill="x", padx=10, pady=5)

            ttk.Label(filter_frame, text="Статус:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
            self.status_filter_var = StringVar()
            self.status_filter_combo = ttk.Combobox(filter_frame,
                                                    textvariable=self.status_filter_var,
                                                    values=["Все", "Новый", "В работе", "Решена", "Закрыта"],
                                                    state="readonly", width=15)
            self.status_filter_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
            self.status_filter_combo.current(0)

            ttk.Label(filter_frame, text="Дата с:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
            self.date_from_var = StringVar()
            self.date_from_entry = ttk.Entry(filter_frame, textvariable=self.date_from_var, width=12)
            self.date_from_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")

            ttk.Label(filter_frame, text="по:").grid(row=0, column=4, padx=5, pady=5, sticky="w")
            self.date_to_var = StringVar()
            self.date_to_entry = ttk.Entry(filter_frame, textvariable=self.date_to_var, width=12)
            self.date_to_entry.grid(row=0, column=5, padx=5, pady=5, sticky="w")

            btn_apply = ttk.Button(filter_frame, text="Применить", command=self.apply_filters)
            btn_apply.grid(row=0, column=6, padx=5, pady=5)

            btn_reset = ttk.Button(filter_frame, text="Сброс", command=self.reset_filters)
            btn_reset.grid(row=0, column=7, padx=5, pady=5)

        # Таблица с заявками
        table_frame = ttk.Frame(self, borderwidth=1, relief="solid", padding=5)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = (
            "id",
            "title",
            "status",
            "category",
            "author",
            "executor",
            "created_at",
            "updated_at",
            "attachment",
        )
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.tree.pack(side="left", fill="both", expand=True)

        headers = (
            "ID",
            "Название",
            "Статус",
            "Категория",
            "Автор",
            "Исполнитель",
            "Создано",
            "Обновлено",
            "Файл",
        )
        for col, header in zip(columns, headers):
            self.tree.heading(col, text=header)
            self.tree.column(col, stretch=True, width=100)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.bind("<Double-Button-1>", self.on_ticket_double_click)

    # ------------------------------------------------------------------
    # Служебные методы
    # ------------------------------------------------------------------

    def _on_close(self) -> None:
        if self.master is not None:
            if hasattr(self.master, "login_var"):
                self.master.login_var.set("")
            if hasattr(self.master, "password_var"):
                self.master.password_var.set("")
            self.destroy()
            self.master.deiconify()
        else:
            self.destroy()

    def load_tickets(self,
                     status_filter: int | None = None,
                     date_from: str | None = None,
                     date_to: str | None = None) -> None:
        """
        Загрузить заявки в таблицу с учётом фильтров.
        """
        for item in self.tree.get_children():
            self.tree.delete(item)

        if self.is_user:
            # Пользователь видит только свои заявки (фильтры ему недоступны)
            tickets = TicketController.get_for_user(self.current_user.id)
        else:
            # Специалист и админ видят все заявки с применением фильтров
            tickets = TicketController.get_filtered(
                status_id=status_filter,
                date_from=date_from,
                date_to=date_to
            )

        for ticket in tickets:
            status_name = getattr(ticket.status_id, "name", "")
            category_title = getattr(ticket.category_id, "title", "")
            author_name = getattr(ticket.user_id, "name", "")
            executor_name = getattr(ticket.executor_id, "name", "") if ticket.executor_id else ""
            created = getattr(ticket, "created_at", "")
            updated = getattr(ticket, "updated_at", "")
            attachment = getattr(ticket, "attachment_path", "") or ""

            self.tree.insert(
                "",
                END,
                values=(
                    ticket.id,
                    ticket.title,
                    status_name,
                    category_title,
                    author_name,
                    executor_name,
                    created,
                    updated,
                    attachment,
                ),
            )

    def _get_selected_ticket_id(self) -> int | None:
        selected = self.tree.selection()
        if not selected:
            return None
        item_id = selected[0]
        values = self.tree.item(item_id, "values")
        if not values:
            return None
        try:
            return int(values[0])
        except (TypeError, ValueError):
            return None

    # ------------------------------------------------------------------
    # Обработчики фильтров
    # ------------------------------------------------------------------

    def apply_filters(self) -> None:
        if self.is_user:
            return

        status_text = self.status_filter_var.get()
        status_map = {
            "Новый": Status.NEW,
            "В работе": Status.IN_PROGRESS,
            "Решена": Status.RESOLVED,
            "Закрыта": Status.CLOSED,
        }
        status_id = status_map.get(status_text) if status_text != "Все" else None
        date_from = self.date_from_var.get().strip() or None
        date_to = self.date_to_var.get().strip() or None

        self.load_tickets(status_filter=status_id, date_from=date_from, date_to=date_to)

    def reset_filters(self) -> None:
        if self.is_user:
            return
        self.status_filter_combo.current(0)
        self.date_from_var.set("")
        self.date_to_var.set("")
        self.load_tickets()

    # ------------------------------------------------------------------
    # Обработчики кнопок
    # ------------------------------------------------------------------

    def on_create_ticket(self) -> None:
        CreateTicketView(self, self.current_user, on_created=self.load_tickets)

    def on_ticket_double_click(self, event) -> None:
        ticket_id = self._get_selected_ticket_id()
        if ticket_id is None:
            return

        ticket = TicketController.get_by_id(ticket_id)
        if ticket is None:
            messagebox.showerror("Заявка", "Заявка не найдена")
            return

        TicketDetailView(self, ticket, self.current_user, on_changed=self.load_tickets)

    def on_open_kb(self) -> None:
        KnowledgeBaseView(self, self.current_user)

    def on_open_users(self) -> None:
        if not self.is_admin:
            return
        UsersView(self)

    def on_open_stats(self) -> None:
        if not self.is_admin:
            return
        StatsView(self)


__all__ = ["MainView"]

