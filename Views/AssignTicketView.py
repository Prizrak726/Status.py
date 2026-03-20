from tkinter import Toplevel, StringVar
from tkinter import ttk, messagebox

from Controllers import TicketController
from Models.Users import Users
from Models.Role import Role
from Models.Ticket import Ticket


class AssignTicketView(Toplevel):
    """
    Окно «Назначение заявки» (по ТЗ — выбор тех. специалиста).
    Доступно только администратору (вызывается из карточки заявки).
    """

    def __init__(self, master, ticket: Ticket, current_user: Users, on_assigned=None) -> None:
        super().__init__(master)
        self.title("Назначение заявки")
        self.geometry("400x200")
        self.resizable(width=False, height=False)

        self.ticket = ticket
        self.current_user = current_user
        self.on_assigned = on_assigned

        self.specialist_var = StringVar()
        self._specialists: list[Users] = []
        self._spec_map: dict[str, int] = {}

        self._load_specialists()
        self._build_ui()

    def _load_specialists(self) -> None:
        """
        Загружаем всех пользователей с ролью «Специалист».
        """
        self._specialists = [
            u for u in Users.select().where(Users.role == Role.SPECIALIST)
        ]
        self._spec_map = {f"{u.name} ({u.login})": int(u.id) for u in self._specialists}

    def _build_ui(self) -> None:
        padding = {"padx": 10, "pady": 5}

        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(frame, text=f"Заявка #{self.ticket.id}:").grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            **padding,
        )

        ttk.Label(frame, text="Выберите специалиста:").grid(
            row=1,
            column=0,
            sticky="w",
            **padding,
        )

        self.combo = ttk.Combobox(
            frame,
            textvariable=self.specialist_var,
            values=list(self._spec_map.keys()),
            state="readonly",
            width=30,
        )
        self.combo.grid(row=1, column=1, sticky="ew", **padding)
        if self._spec_map:
            self.combo.current(0)

        btn_assign = ttk.Button(frame, text="Назначить", command=self.on_assign)
        btn_assign.grid(row=2, column=0, sticky="ew", padx=10, pady=(15, 5))

        btn_cancel = ttk.Button(frame, text="Отмена", command=self.destroy)
        btn_cancel.grid(row=2, column=1, sticky="ew", padx=10, pady=(15, 5))

    def on_assign(self) -> None:
        if not self._spec_map:
            messagebox.showwarning("Назначение", "Нет доступных специалистов")
            return

        label = self.specialist_var.get().strip()
        executor_id = self._spec_map.get(label)
        if executor_id is None:
            messagebox.showwarning("Назначение", "Выберите специалиста")
            return

        ok, msg = TicketController.assign_executor(self.ticket.id, executor_id)
        if not ok:
            messagebox.showerror("Назначение", msg)
            return

        messagebox.showinfo("Назначение", "Заявка успешно назначена специалисту")
        if callable(self.on_assigned):
            self.on_assigned()
        self.destroy()


__all__ = ["AssignTicketView"]

