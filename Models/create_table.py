from Models.Users import Users
from Models.ArticleBase import ArticleBase
from Models.Base import *
from Models.Category import Category
from Models.Comment import Comment
from Models.Role import Role
from Models.Status import Status
from Models.Ticket import Ticket
from Models.Type import Type


def create_tables():
    connect().create_tables(
        [
            Users,
            Type,
            Comment,
            Role,
            Status,
            Ticket,
            Category,
            ArticleBase,
        ]
    )


def seed_roles():
    default_roles = [
        (Role.USER, "Пользователь"),
        (Role.SPECIALIST, "Специалист"),
        (Role.ADMIN, "Администратор"),
    ]

    for role_id, name in default_roles:
        Role.get_or_create(id=role_id, defaults={"name": name})


def seed_statuses():
    default_statuses = [
        (Status.NEW, "Новый"),
        (Status.IN_PROGRESS, "В работе"),
        (Status.RESOLVED, "Решена"),
        (Status.CLOSED, "Закрыта"),
    ]

    for status_id, name in default_statuses:
        Status.get_or_create(id=status_id, defaults={"name": name})


def seed_categories():
    default_categories = [
        (Category.INCIDENT, "Инцидент", "Что-то сломалось (ПК, принтер, сеть и т.п.)"),
        (Category.MAINTENANCE, "Обслуживание оборудования", "Настройка, ремонт, перенос, подключение оборудования"),
        (Category.SOFTWARE, "Установка/обновление ПО", "Установка программ, драйверов, обновлений"),
        (Category.ACCESS, "Проблемы с доступом", "Логин/пароль, права, доступ к системам"),
        (Category.CONSULTING, "Консультация", "Вопросы по использованию систем и ПО"),
        (Category.IMPROVEMENT, "Запрос на доработку", "Изменение настроек, добавление функционала"),
        (Category.ACCOUNT, "Работа с учетными записями", "Создание/изменение/блокировка учеток"),
        (Category.INFORMATION, "Информационная поддержка", "Сайт, СДО, отчётность, электронный журнал"),
        (Category.OTHER, "Другое", "Прочие обращения"),
    ]

    for cat_id, title, description in default_categories:
        Category.get_or_create(
            id=cat_id,
            defaults={
                "title": title,
                "description": description,
            },
        )
def seed_types():
    default_types = [
        (Type.PUBLIC, "Публичный"),
        (Type.INTERNAL, "Внутренний"),
    ]
    for type_id, name in default_types:
        Type.get_or_create(id=type_id, defaults={"name": name})


if __name__ == "__main__":
    create_tables()
    seed_roles()
    seed_statuses()
    seed_categories()
    seed_types()