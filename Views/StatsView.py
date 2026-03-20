from tkinter import Toplevel
from tkinter import ttk

from Controllers import StatisticsController


class StatsView(Toplevel):
    """
    Окно «Статистика» по макету:
    показывает количество созданных, выполненных и находящихся в процессе заявок.
    """

    def __init__(self, master) -> None:
        super().__init__(master)
        self.title("Статистика")
        self.geometry("400x200")
        self.resizable(width=False, height=False)

        self._build_ui()
        self._load_stats()

    def _build_ui(self) -> None:
        padding = {"padx": 10, "pady": 5}

        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Заявок создано
        self.lbl_created = ttk.Label(frame, text="Заявок создано: 0")
        self.lbl_created.grid(row=0, column=0, sticky="w", **padding)

        # Выполненные
        self.lbl_done = ttk.Label(frame, text="Выполненные: 0")
        self.lbl_done.grid(row=1, column=0, sticky="w", **padding)

        # В процессе
        self.lbl_in_progress = ttk.Label(frame, text="В процессе: 0")
        self.lbl_in_progress.grid(row=2, column=0, sticky="w", **padding)

        btn_back = ttk.Button(frame, text="Назад", command=self.destroy)
        btn_back.grid(row=3, column=0, sticky="ew", padx=10, pady=(15, 5))

    def _load_stats(self) -> None:
        stats = StatisticsController.get_global_statistics()
        # По макету: "Заявок создано", "Выполненные", "В процессе"
        self.lbl_created.config(text=f"Заявок создано: {stats.total}")
        self.lbl_done.config(text=f"Выполненные: {stats.done}")
        self.lbl_in_progress.config(text=f"В процессе: {stats.in_progress}")


__all__ = ["StatsView"]

