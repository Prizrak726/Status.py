from Models.Base import *


class Category(BaseModel):
    # Фиксированные категории заявок
    INCIDENT = 1        # Инцидент (что-то сломалось)
    MAINTENANCE = 2     # Обслуживание оборудования
    SOFTWARE = 3        # Установка/обновление ПО
    ACCESS = 4          # Проблемы с доступом
    CONSULTING = 5      # Консультация
    IMPROVEMENT = 6     # Запрос на доработку/изменение
    ACCOUNT = 7         # Работа с учетными записями
    INFORMATION = 8     # Информационная поддержка
    OTHER = 9           # Другое

    id = PrimaryKeyField(primary_key=True)
    title = TextField(unique=True)
    description = TextField(null=True)

    class Meta:
        table_name = "category"