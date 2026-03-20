from tkinter import Toplevel, Text, StringVar, END
from tkinter import ttk, messagebox

from Controllers import TicketController, CommentController, ArticleController
from Models.Users import Users
from Models.Role import Role
from Models.Status import Status
from Models.Ticket import Ticket

from Views.ArticleCreateView import ArticleCreateView
from Views.AssignTicketView import AssignTicketView


class TicketDetailView(Toplevel):
    """
    Окно «Заявка» с комментариями, завершением и созданием статьи,
    а также возможностью смены статуса (для специалистов/админов).
    """

    def __init__(self, master, ticket: Ticket, current_user: Users, on_changed=None) -> None:
        super().__init__(master)
        self.title(f"Заявка #{ticket.id}")
        self.geometry("800x650")
        self.resizable(width=True, height=True)

        self.ticket = ticket
        self.current_user = current_user
        self.on_changed = on_changed

        role_id = int(current_user.role_id)
        self.is_admin = role_id == Role.ADMIN
        self.is_admin_or_specialist = role_id in (Role.ADMIN, Role.SPECIALIST)

        self.comment_var = StringVar()

        self._build_ui()
        self._load_ticket_info()
        self._load_comments()

    def _build_ui(self) -> None:
        padding = {"padx": 10, "pady": 5}

        # Информация о заявке
        info_frame = ttk.Frame(self)
        info_frame.pack(fill="x", padx=10, pady=10)

        self.lbl_title = ttk.Label(info_frame, text="", font=("TkDefaultFont", 12, "bold"))
        self.lbl_title.grid(row=0, column=0, columnspan=2, sticky="w", **padding)

        self.lbl_status = ttk.Label(info_frame, text="")
        self.lbl_status.grid(row=1, column=0, sticky="w", **padding)

        self.lbl_category = ttk.Label(info_frame, text="")
        self.lbl_category.grid(row=1, column=1, sticky="w", **padding)

        self.lbl_author = ttk.Label(info_frame, text="")
        self.lbl_author.grid(row=2, column=0, sticky="w", **padding)

        self.lbl_executor = ttk.Label(info_frame, text="")
        self.lbl_executor.grid(row=2, column=1, sticky="w", **padding)

        self.lbl_dates = ttk.Label(info_frame, text="")
        self.lbl_dates.grid(row=3, column=0, columnspan=2, sticky="w", **padding)

        ttk.Label(self, text="Описание:").pack(anchor="w", padx=10)
        self.description_text = Text(self, height=6, wrap="word")
        self.description_text.pack(fill="x", padx=10, pady=(0, 10))
        self.description_text.config(state="disabled")

        # Комментарии
        comments_frame = ttk.Labelframe(self, text="Комментарии")
        comments_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.comments_text = Text(comments_frame, height=8, wrap="word")
        self.comments_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.comments_text.config(state="disabled")

        add_frame = ttk.Frame(comments_frame)
        add_frame.pack(fill="x", padx=5, pady=5)

        entry = ttk.Entry(add_frame, textvariable=self.comment_var)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        btn_add_comment = ttk.Button(add_frame, text="Добавить комментарий", command=self.on_add_comment)
        btn_add_comment.pack(side="right")

        # Панель смены статуса (только для специалиста/админа)
        if self.is_admin_or_specialist:
            status_frame = ttk.LabelFrame(self, text="Изменить статус")
            status_frame.pack(fill="x", padx=10, pady=5)

            ttk.Label(status_frame, text="Новый статус:").pack(side="left", padx=5)
            self.status_var = StringVar()
            self.status_combo = ttk.Combobox(status_frame, textvariable=self.status_var,
                                             values=["Новый", "В работе", "Решена", "Закрыта"],
                                             state="readonly", width=15)
            self.status_combo.pack(side="left", padx=5)

            btn_change_status = ttk.Button(status_frame, text="Применить", command=self.on_change_status)
            btn_change_status.pack(side="left", padx=5)

        # Нижние кнопки
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill="x", padx=10, pady=10)

        btn_back = ttk.Button(bottom_frame, text="Назад", command=self.destroy)
        btn_back.pack(side="left", padx=5)

        if self.is_admin:
            self.btn_assign = ttk.Button(bottom_frame, text="Назначить", command=self.on_assign)
            self.btn_assign.pack(side="left", padx=5)

        self.btn_finish = ttk.Button(bottom_frame, text="Отметить как решённую", command=self.on_finish)
        self.btn_finish.pack(side="left", padx=5)

        btn_article = ttk.Button(bottom_frame, text="Создать статью", command=self.on_create_article)
        btn_article.pack(side="left", padx=5)

    def _load_ticket_info(self) -> None:
        ticket = self.ticket
        self.lbl_title.config(text=ticket.title)

        status_name = getattr(ticket.status_id, "name", "")
        category_title = getattr(ticket.category_id, "title", "")
        author_name = getattr(ticket.user_id, "name", "")
        executor_name = getattr(ticket.executor_id, "name", "") if ticket.executor_id else ""

        self.lbl_status.config(text=f"Статус: {status_name}")
        self.lbl_category.config(text=f"Категория: {category_title}")
        self.lbl_author.config(text=f"Автор: {author_name}")
        self.lbl_executor.config(text=f"Исполнитель: {executor_name}")

        created = getattr(ticket, "created_at", "")
        updated = getattr(ticket, "updated_at", "")
        self.lbl_dates.config(text=f"Создано: {created} | Обновлено: {updated}")

        self.description_text.config(state="normal")
        self.description_text.delete("1.0", END)
        self.description_text.insert("1.0", ticket.description)
        self.description_text.config(state="disabled")

        # Устанавливаем текущий статус в комбобокс, если он есть
        if self.is_admin_or_specialist:
            current_status = status_name
            self.status_var.set(current_status)

    def _load_comments(self) -> None:
        self.comments_text.config(state="normal")
        self.comments_text.delete("1.0", END)

        comments = CommentController.get_for_ticket(self.ticket.id, self.current_user.id)
        for comment in comments:
            author_name = getattr(comment.user_id, "name", "")
            line = f"{author_name}: {comment.description}\n"
            self.comments_text.insert(END, line)

        self.comments_text.config(state="disabled")

    # ------------------------------------------------------------------
    # Обработчики
    # ------------------------------------------------------------------

    def on_add_comment(self) -> None:
        text = self.comment_var.get().strip()
        if not text:
            return

        ok, result = CommentController.add_comment(
            ticket_id=self.ticket.id,
            user_id=self.current_user.id,
            description=text,
        )
        if not ok:
            messagebox.showerror("Комментарий", str(result))
            return

        self.comment_var.set("")
        self._load_comments()

    def on_change_status(self) -> None:
        new_status_name = self.status_var.get()
        status_map = {
            "Новый": Status.NEW,
            "В работе": Status.IN_PROGRESS,
            "Решена": Status.RESOLVED,
            "Закрыта": Status.CLOSED,
        }
        new_status_id = status_map.get(new_status_name)
        if new_status_id is None:
            return

        ok, msg = TicketController.set_status(self.ticket.id, new_status_id)
        if not ok:
            messagebox.showerror("Ошибка", msg)
            return

        # Обновить отображение
        updated_ticket = TicketController.get_by_id(self.ticket.id)
        if updated_ticket:
            self.ticket = updated_ticket
            self._load_ticket_info()
            if callable(self.on_changed):
                self.on_changed()
            messagebox.showinfo("Статус", "Статус заявки изменён")

    def on_finish(self) -> None:
        is_executor = self.ticket.executor_id and int(self.ticket.executor_id.id) == int(self.current_user.id)
        if not (self.is_admin_or_specialist or is_executor):
            messagebox.showwarning("Завершение", "Только исполнитель или специалист/админ могут завершить заявку")
            return

        ok, msg = TicketController.finish_ticket(self.ticket.id)
        if not ok:
            messagebox.showerror("Завершение", msg)
            return

        updated_ticket = TicketController.get_by_id(self.ticket.id)
        if updated_ticket:
            self.ticket = updated_ticket
            self._load_ticket_info()
            if callable(self.on_changed):
                self.on_changed()
            messagebox.showinfo("Завершение", "Заявка отмечена как решённая.")

    def on_assign(self) -> None:
        if not self.is_admin:
            return

        AssignTicketView(self, self.ticket, self.current_user, on_assigned=self._on_assigned)

    def _on_assigned(self) -> None:
        updated_ticket = TicketController.get_by_id(self.ticket.id)
        if updated_ticket:
            self.ticket = updated_ticket
            self._load_ticket_info()
            if callable(self.on_changed):
                self.on_changed()

    def on_create_article(self) -> None:
        ArticleCreateView(self, self.ticket, self.current_user)


__all__ = ["TicketDetailView"]

