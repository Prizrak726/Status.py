from typing import Iterable

from peewee import DoesNotExist

from Models.Comment import Comment
from Models.Type import Type
from Models.Users import Users
from Models.Ticket import Ticket
from Models.Role import Role


class CommentController:
    """
    Контроллер для работы с комментариями к заявкам.
    """

    @classmethod
    def add_comment(
        cls,
        ticket_id: int,
        user_id: int,
        description: str,
        type_id: int | None = None,
    ) -> tuple[bool, str | Comment]:
        """
        Добавить комментарий к заявке.
        По умолчанию создаётся публичный комментарий.
        """
        try:
            ticket = Ticket.get_by_id(ticket_id)
        except DoesNotExist:
            return False, "Заявка не найдена"

        try:
            user = Users.get_by_id(user_id)
        except DoesNotExist:
            return False, "Пользователь не найден"

        if type_id is None:
            type_id = Type.PUBLIC

        try:
            comment = Comment.create(
                description=description,
                user_id=user,
                ticket_id=ticket,
                type_id=type_id,
            )
            return True, comment
        except Exception as exc:  # noqa: BLE001
            return False, f"Ошибка добавления комментария: {exc}"

    @classmethod
    def get_for_ticket(
        cls,
        ticket_id: int,
        current_user_id: int | None = None,
    ) -> Iterable[Comment]:
        """
        Получить комментарии по заявке.

        Если пользователь — обычный (Role.USER), внутренние комментарии скрываются.
        Для специалистов и админов показываются все.
        """
        base_query = Comment.select().where(Comment.ticket_id == ticket_id)

        if current_user_id is None:
            # если нет информации о пользователе, показываем только публичные
            return base_query.where(Comment.type_id == Type.PUBLIC)

        try:
            user = Users.get_by_id(current_user_id)
        except DoesNotExist:
            # если пользователя не нашли, безопасно отдать только публичные
            return base_query.where(Comment.type_id == Type.PUBLIC)

        role_id = int(user.role_id)
        if role_id in (Role.SPECIALIST, Role.ADMIN):
            return base_query

        return base_query.where(Comment.type_id == Type.PUBLIC)


__all__ = ["CommentController"]

