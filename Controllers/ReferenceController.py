from typing import Iterable

from Models.Category import Category
from Models.Status import Status
from Models.Role import Role
from Models.Type import Type


class ReferenceController:
    """
    Контроллер для справочников (категории, роли, статусы, типы комментариев).
    Удобно использовать для заполнения выпадающих списков в окнах.
    """

    @classmethod
    def get_categories(cls) -> Iterable[Category]:
        """
        Все категории заявок.
        """
        return Category.select().order_by(Category.title.asc())

    @classmethod
    def get_statuses(cls) -> Iterable[Status]:
        """
        Все статусы заявок.
        """
        return Status.select().order_by(Status.id.asc())

    @classmethod
    def get_roles(cls) -> Iterable[Role]:
        """
        Все роли пользователей.
        """
        return Role.select().order_by(Role.id.asc())

    @classmethod
    def get_comment_types(cls) -> Iterable[Type]:
        """
        Типы комментариев (публичный/внутренний).
        """
        return Type.select().order_by(Type.id.asc())


__all__ = ["ReferenceController"]

