from tkinter import Toplevel, END
from tkinter import ttk, messagebox

from Controllers import UserController


class UsersView(Toplevel):
    """
    Окно «Пользователи» – список и удаление пользователей.
    """

    def __init__(self, master) -> None:
        super().__init__(master)
        self.title("Пользователи")
        self.geometry("700x400")
        self.resizable(width=True, height=True)

        self._build_ui()
        self.load_users()

    def _build_ui(self) -> None:
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", padx=10, pady=5)

        btn_delete = ttk.Button(top_frame, text="Удалить", command=self.on_delete)
        btn_delete.pack(side="right", padx=5)

        btn_back = ttk.Button(top_frame, text="Назад", command=self.destroy)
        btn_back.pack(side="right", padx=5)

        table_frame = ttk.Frame(self, borderwidth=1, relief="solid", padding=5)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("id", "login", "name", "role")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.tree.pack(side="left", fill="both", expand=True)

        headers = ("ID", "Логин", "Имя", "Роль")
        for col, header in zip(columns, headers):
            self.tree.heading(col, text=header)
            self.tree.column(col, stretch=True, width=120)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

    def load_users(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

        users = UserController.list_users()
        for user in users:
            role_name = getattr(user.role, "name", "")
            self.tree.insert(
                "",
                END,
                values=(user.id, user.login, user.name, role_name),
            )

    def _get_selected_user_id(self) -> int | None:
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

    def on_delete(self) -> None:
        user_id = self._get_selected_user_id()
        if user_id is None:
            messagebox.showwarning("Удаление", "Выберите пользователя")
            return

        if messagebox.askyesno("Удаление", "Удалить выбранного пользователя?"):
            ok, msg = UserController.delete_user(user_id)
            if not ok:
                messagebox.showerror("Удаление", msg)
                return
            self.load_users()


__all__ = ["UsersView"]

