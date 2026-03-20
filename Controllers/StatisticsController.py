from dataclasses import dataclass
from Models.Ticket import Ticket
from Models.Status import Status
from Models.Category import Category
from Models.Users import Users


@dataclass
class TicketStatistics:
    total: int
    new: int
    in_progress: int
    done: int          # суммарно решённые и закрытые


class StatisticsController:
    """
    Контроллер для получения статистики по заявкам.
    """

    @classmethod
    def get_global_statistics(cls) -> TicketStatistics:
        """
        Общая статистика по всем заявкам:
        - всего
        - новые
        - в работе
        - завершённые (решёные + закрытые)
        """
        total = Ticket.select().count()
        new_cnt = Ticket.select().where(Ticket.status_id == Status.NEW).count()
        in_progress = Ticket.select().where(Ticket.status_id == Status.IN_PROGRESS).count()
        # завершённые: решена (RESOLVED) или закрыта (CLOSED)
        done = Ticket.select().where(Ticket.status_id.in_([Status.RESOLVED, Status.CLOSED])).count()

        return TicketStatistics(
            total=total,
            new=new_cnt,
            in_progress=in_progress,
            done=done,
        )

    @classmethod
    def get_user_statistics(cls, user_id: int) -> TicketStatistics:
        """
        Статистика по заявкам конкретного пользователя (как автора).
        """
        total = Ticket.select().where(Ticket.user_id == user_id).count()
        new_cnt = (
            Ticket.select()
            .where((Ticket.user_id == user_id) & (Ticket.status_id == Status.NEW))
            .count()
        )
        in_progress = (
            Ticket.select()
            .where((Ticket.user_id == user_id) & (Ticket.status_id == Status.IN_PROGRESS))
            .count()
        )
        done = (
            Ticket.select()
            .where((Ticket.user_id == user_id) & (Ticket.status_id.in_([Status.RESOLVED, Status.CLOSED])))
            .count()
        )

        return TicketStatistics(
            total=total,
            new=new_cnt,
            in_progress=in_progress,
            done=done,
        )

    @classmethod
    def get_by_category(cls) -> list[tuple[str, int]]:
        """
        Количество заявок по категориям.
        """
        query = (
            Ticket.select(Category.title, Ticket.id.count())
            .join(Category)
            .group_by(Category.id)
            .order_by(Ticket.id.count().desc())
        )
        return [(row.category_id.title, row.count) for row in query]

    @classmethod
    def get_load_by_specialist(cls) -> list[tuple[str, int]]:
        """
        Загрузка специалистов: количество открытых (не завершённых) заявок на каждого.
        """
        open_statuses = [Status.NEW, Status.IN_PROGRESS]
        query = (
            Ticket.select(Users.name, Ticket.id.count())
            .join(Users, on=(Ticket.executor_id == Users.id))
            .where(Ticket.status_id.in_(open_statuses))
            .group_by(Users.id)
            .order_by(Ticket.id.count().desc())
        )
        return [(row.executor_id.name, row.count) for row in query]


__all__ = ["StatisticsController", "TicketStatistics"]


