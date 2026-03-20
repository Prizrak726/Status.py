from typing import Iterable, Optional

from peewee import DoesNotExist

from Models.ArticleBase import ArticleBase
from Models.Ticket import Ticket
from Models.Users import Users


class ArticleController:
    """
    Контроллер для работы с базой знаний (ArticleBase).
    """

    @classmethod
    def get_all(cls) -> Iterable[ArticleBase]:
        """
        Получить все статьи.
        """
        return ArticleBase.select().order_by(ArticleBase.id.desc())

    @classmethod
    def get_by_id(cls, article_id: int) -> Optional[ArticleBase]:
        """
        Получить статью по id.
        """
        try:
            return ArticleBase.get_by_id(article_id)
        except DoesNotExist:
            return None

    @classmethod
    def get_for_ticket(cls, ticket_id: int) -> Iterable[ArticleBase]:
        """
        Статьи, связанные с определённой заявкой.
        """
        return ArticleBase.select().where(ArticleBase.ticket_id == ticket_id)

    @classmethod
    def search_by_title(cls, query: str) -> Iterable[ArticleBase]:
        """
        Поиск статей по названию (используется на форме «Поиск по названию»).
        """
        like_expr = f"%{query}%"
        return ArticleBase.select().where(ArticleBase.title.contains(query) | (ArticleBase.title ** like_expr))

    @classmethod
    def create_article(
        cls,
        title: str,
        description: str,
        ticket_id: int,
        executor_id: int,
    ) -> tuple[bool, str | ArticleBase]:
        """
        Создать новую статью базы знаний.
        Как правило, вызывается из формы заявки («Создать статью»).
        """
        try:
            ticket = Ticket.get_by_id(ticket_id)
        except DoesNotExist:
            return False, "Заявка не найдена"

        try:
            executor = Users.get_by_id(executor_id)
        except DoesNotExist:
            return False, "Исполнитель не найден"

        try:
            article = ArticleBase.create(
                title=title,
                description=description,
                ticket_id=ticket,
                executor_id=executor,
            )
            return True, article
        except Exception as exc:  # noqa: BLE001
            return False, f"Ошибка создания статьи: {exc}"

    @classmethod
    def delete_article(cls, article_id: int) -> tuple[bool, str]:
        """
        Удалить статью (кнопка «Удалить» в экране базы знаний).
        """
        try:
            article = ArticleBase.get_by_id(article_id)
        except DoesNotExist:
            return False, "Статья не найдена"

        try:
            article.delete_instance()
            return True, "Статья удалена"
        except Exception as exc:  # noqa: BLE001
            return False, f"Ошибка удаления статьи: {exc}"


__all__ = ["ArticleController"]

