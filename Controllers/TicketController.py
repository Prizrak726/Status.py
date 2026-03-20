from typing import Iterable, Optional

from peewee import DoesNotExist

from Models.Ticket import Ticket
from Models.Status import Status
from Models.Category import Category
from Models.Users import Users


class TicketController:
    """
    Контроллер для работы с заявками.
    """

    # ------------------------------------------------------------------
    # Базовые выборки
    # ------------------------------------------------------------------

    @classmethod
    def get_all(cls) -> Iterable[Ticket]:
        """
        Получить все заявки.
        """
        return Ticket.select().order_by(Ticket.created_at.desc())

    @classmethod
    def get_by_id(cls, ticket_id: int) -> Optional[Ticket]:
        """
        Получить заявку по id.
        """
        try:
            return Ticket.get_by_id(ticket_id)
        except DoesNotExist:
            return None

    @classmethod
    def get_for_user(cls, user_id: int) -> Iterable[Ticket]:
        """
        Заявки, созданные пользователем.
        """
        return (
            Ticket.select()
            .where(Ticket.user_id == user_id)
            .order_by(Ticket.created_at.desc())
        )

    @classmethod
    def get_for_executor(cls, executor_id: int) -> Iterable[Ticket]:
        """
        Заявки, назначенные исполнителю.
        """
        return (
            Ticket.select()
            .where(Ticket.executor_id == executor_id)
            .order_by(Ticket.created_at.desc())
        )

    @classmethod
    def get_by_status(cls, status_id: int) -> Iterable[Ticket]:
        """
        Заявки по статусу.
        """
        return (
            Ticket.select()
            .where(Ticket.status_id == status_id)
            .order_by(Ticket.created_at.desc())
        )

    # ------------------------------------------------------------------
    # Создание и изменение
    # ------------------------------------------------------------------

    @classmethod
    def create_ticket(
            cls,
            title: str,
            description: str,
            category_id: int,
            user_id: int,
            executor_id: Optional[int] = None,
            attachment_path: Optional[str] = None,  # новый параметр
    ) -> tuple[bool, str | Ticket]:
        try:
            Category.get_by_id(category_id)
        except DoesNotExist:
            return False, "Указанная категория не найдена"

        try:
            user = Users.get_by_id(user_id)
        except DoesNotExist:
            return False, "Пользователь (автор заявки) не найден"

        if executor_id is not None:
            try:
                Users.get_by_id(executor_id)
            except DoesNotExist:
                return False, "Указанный исполнитель не найден"

        try:
            ticket = Ticket.create(
                title=title,
                description=description,
                status_id=Status.NEW,
                user_id=user.id,
                executor_id=executor_id,
                category_id=category_id,
                attachment_path=attachment_path,  # сохраняем путь к файлу
            )
            return True, ticket
        except Exception as exc:
            return False, f"Ошибка создания заявки: {exc}"

    @classmethod
    def update_ticket(cls, ticket_id: int, **fields) -> tuple[bool, str]:
        """
        Обновить поля заявки (title, description, category_id и т.п.).
        """
        try:
            ticket = Ticket.get_by_id(ticket_id)
        except DoesNotExist:
            return False, "Заявка не найдена"

        # Не даём напрямую менять user_id / executor_id / status_id здесь,
        # для этого есть отдельные методы.
        forbidden = {"user_id", "executor_id", "status_id", "id"}
        for field_name, value in fields.items():
            if field_name in forbidden:
                continue
            if hasattr(ticket, field_name):
                setattr(ticket, field_name, value)

        try:
            ticket.save()
            return True, "Заявка обновлена"
        except Exception as exc:  # noqa: BLE001
            return False, f"Ошибка обновления заявки: {exc}"

    @classmethod
    def set_status(cls, ticket_id: int, status_id: int) -> tuple[bool, str]:
        """
        Изменить статус заявки.
        """
        try:
            ticket = Ticket.get_by_id(ticket_id)
        except DoesNotExist:
            return False, "Заявка не найдена"

        try:
            Status.get_by_id(status_id)
        except DoesNotExist:
            return False, "Статус не найден"

        try:
            ticket.status_id = status_id
            ticket.save()
            return True, "Статус заявки обновлён"
        except Exception as exc:  # noqa: BLE001
            return False, f"Ошибка изменения статуса: {exc}"

    @classmethod
    def assign_executor(cls, ticket_id: int, executor_id: int) -> tuple[bool, str]:
        """
        Назначить исполнителя на заявку.
        """
        try:
            ticket = Ticket.get_by_id(ticket_id)
        except DoesNotExist:
            return False, "Заявка не найдена"

        try:
            executor = Users.get_by_id(executor_id)
        except DoesNotExist:
            return False, "Исполнитель не найден"

        ticket.executor_id = executor
        # при назначении переводим в статус «В работе»
        ticket.status_id = Status.IN_PROGRESS

        try:
            ticket.save()
            return True, "Исполнитель назначен"
        except Exception as exc:  # noqa: BLE001
            return False, f"Ошибка назначения исполнителя: {exc}"

    @classmethod
    def finish_ticket(cls, ticket_id: int) -> tuple[bool, str]:
        """
        Завершить заявку (перевести в статус «Решена»).
        """
        return cls.set_status(ticket_id, Status.RESOLVED)

    @classmethod
    def delete_ticket(cls, ticket_id: int) -> tuple[bool, str]:
        """
        Удалить заявку.
        """
        try:
            ticket = Ticket.get_by_id(ticket_id)
        except DoesNotExist:
            return False, "Заявка не найдена"

        try:
            ticket.delete_instance()
            return True, "Заявка удалена"
        except Exception as exc:  # noqa: BLE001
            return False, f"Ошибка удаления заявки: {exc}"

    @classmethod
    def get_filtered(cls, status_id: Optional[int] = None,
                     date_from: Optional[str] = None,
                     date_to: Optional[str] = None) -> Iterable[Ticket]:
        """
        Получить заявки с фильтрацией по статусу и диапазону дат (created_at).
        """
        query = Ticket.select().order_by(Ticket.created_at.desc())
        if status_id is not None:
            query = query.where(Ticket.status_id == status_id)
        if date_from:
            query = query.where(Ticket.created_at >= date_from)
        if date_to:
            # Добавляем конец дня, чтобы включить все заявки за указанную дату
            from datetime import datetime, timedelta
            dt_to = datetime.strptime(date_to, "%Y-%m-%d") + timedelta(days=1)
            query = query.where(Ticket.created_at < dt_to)
        return query


__all__ = ["TicketController"]

