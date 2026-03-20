from tkinter import Toplevel, StringVar
from tkinter import ttk, messagebox

from Controllers.UserController import UserController
from Controllers.ReferenceController import ReferenceController


class RegView(Toplevel):
    """
    Окно регистрации пользователя.
    """

    def __init__(self, master=None) -> None:
        super().__init__(master)
        self.title("Регистрация")
        self.geometry("350x400")
        self.resizable(width=False, height=False)

        self.name_var = StringVar()
        self.login_var = StringVar()
        self.password_var = StringVar()
        self.password2_var = StringVar()
        self.role_var = StringVar()

        self._roles = []
        self._role_map: dict[str, int] = {}

        self._load_roles()
        self._build_ui()

    def _load_roles(self) -> None:
        """
        Загружаем роли из БД для combobox.
        """
        try:
            # Пытаемся получить роли через справочник
            roles = list(ReferenceController.get_roles())
            if not roles:
                # Если таблица пуста, пробуем заполнить через seed
                from Models.create_table import seed_roles
                seed_roles()
                roles = list(ReferenceController.get_roles())

            self._roles = roles
            self._role_map = {role.name: int(role.id) for role in self._roles}

            # Если после всех попыток ролей нет, показываем ошибку
            if not self._role_map:
                messagebox.showerror("Ошибка", "Не удалось загрузить список ролей. Проверьте базу данных.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки ролей: {e}")
            self._roles = []
            self._role_map = {}

    def _build_ui(self) -> None:
        padding = {"padx": 20, "pady": 5}

        container = ttk.Frame(self)
        container.pack(expand=True)

        # Имя
        ttk.Label(container, text="Имя:").pack(anchor="w", **padding)
        name_entry = ttk.Entry(container, textvariable=self.name_var, width=30)
        name_entry.pack(fill="x", padx=20)

        # Логин
        ttk.Label(container, text="Логин:").pack(anchor="w", **padding)
        login_entry = ttk.Entry(container, textvariable=self.login_var, width=30)
        login_entry.pack(fill="x", padx=20)

        # Роль
        ttk.Label(container, text="Роль:").pack(anchor="w", **padding)
        role_combo = ttk.Combobox(
            container,
            textvariable=self.role_var,
            values=list(self._role_map.keys()),
            state="readonly",
            width=28,
        )
        role_combo.pack(fill="x", padx=20)
        if self._role_map:
            role_combo.current(0)

        # Пароль
        ttk.Label(container, text="Пароль:").pack(anchor="w", **padding)
        password_entry = ttk.Entry(container, textvariable=self.password_var, width=30, show="*")
        password_entry.pack(fill="x", padx=20)

        # Повтор пароля
        ttk.Label(container, text="Повтор пароля:").pack(anchor="w", **padding)
        password2_entry = ttk.Entry(container, textvariable=self.password2_var, width=30, show="*")
        password2_entry.pack(fill="x", padx=20)

        # Кнопки
        btn_reg = ttk.Button(container, text="Зарегистрироваться", command=self.on_register)
        btn_reg.pack(fill="x", padx=20, pady=(15, 5))

        name_entry.focus_set()

    def on_register(self) -> None:
        name = self.name_var.get().strip()
        login = self.login_var.get().strip()
        password = self.password_var.get().strip()
        password2 = self.password2_var.get().strip()
        role_name = self.role_var.get().strip()

        if not all([login, password, password2, role_name]):
            messagebox.showwarning("Регистрация", "Заполните логин, пароль и роль")
            return

        if len(login) > 10:
            messagebox.showwarning("Регистрация", "Логин не должен превышать 10 символов")
            return

        if password != password2:
            messagebox.showwarning("Регистрация", "Пароли не совпадают")
            return

        role_id = self._role_map.get(role_name)
        if role_id is None:
            messagebox.showerror("Регистрация", "Роль не выбрана или не найдена")
            return

        ok, result = UserController.register(
            name=name,
            login=login,
            password=password,
            role_id=role_id,
        )
        if not ok:
            messagebox.showerror("Регистрация", str(result))
            return

        messagebox.showinfo("Регистрация", "Пользователь успешно зарегистрирован")
        self.destroy()


if __name__ == "__main__":
    from tkinter import Tk

    root = Tk()
    root.withdraw()
    win = RegView(root)
    win.mainloop()