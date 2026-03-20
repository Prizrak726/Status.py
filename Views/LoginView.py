from tkinter import Tk, StringVar, END
from tkinter import ttk, messagebox

from Controllers.UserController import UserController
from Views.RegView import RegView
from Views.MainView import MainView


class LoginView(Tk):
    """
    Окно входа в систему.
    """

    def __init__(self) -> None:
        super().__init__()
        self.title("Вход")
        self.geometry("400x220")
        self.resizable(width=False, height=False)

        self.login_var = StringVar()
        self.password_var = StringVar()

        self._build_ui()

    def _build_ui(self) -> None:
        padding = {"padx": 10, "pady": 5}

        ttk.Label(self, text="Логин:").pack()
        login_entry = ttk.Entry(self, textvariable=self.login_var, width=30)
        login_entry.pack()

        ttk.Label(self, text="Пароль:").pack()
        password_entry = ttk.Entry(self, textvariable=self.password_var, width=30, show="*")
        password_entry.pack(padx=5, pady=5)

        btn_reg = ttk.Button(self, text="Регистрация", command=self.open_registration)
        btn_reg.pack(padx=5, pady=5)

        btn_login = ttk.Button(self, text="Вход", command=self.on_login)
        btn_login.pack(padx=5, pady=5)

        # Фокус на поле логина
        login_entry.focus_set()

    def on_login(self) -> None:
        login = self.login_var.get().strip()
        password = self.password_var.get().strip()

        if not login or not password:
            messagebox.showwarning("Вход", "Введите логин и пароль")
            return

        user = UserController.authenticate(login=login, password=password)
        if user is None:
            messagebox.showerror("Вход", "Неверный логин или пароль")
            return

        # открываем главное окно с заявками
        MainView(self, user)
        # очищаем пароль и прячем окно входа
        self.password_var.set("")
        self.withdraw()

    def open_registration(self) -> None:
        """
        Открыть окно регистрации поверх окна входа.
        """
        RegView(self)


if __name__ == "__main__":
    app = LoginView()
    app.mainloop()

